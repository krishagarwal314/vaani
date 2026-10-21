"""CallSession: runs one call through the 9-stage state machine.

Order of precedence for every user turn:
  1. deterministic guardrails (do-not-call, not interested, "are you a bot?")
  2. pending amount read-back confirmation
  3. LLM step (structured output) -> slot merge -> validated stage transition -> stage entry line
The same session object is driven by the text CLI and the LiveKit voice worker.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from agent.guardrails import is_bot_question, is_do_not_call, is_not_interested
from agent.lang import detect_lang, is_affirm, is_deny
from agent.llm.base import LLM
from agent.numbers import parse_amount, rupees_words
from agent.prompts import build_system_prompt, prompt_version
from agent.responses import render
from agent.schema import AMOUNT_SLOTS, Intent, LLMRequest, LLMTurnOutput, Slots, ToolCall
from agent.stages import STAGE_TOOLS, TRANSITIONS, Stage, check_transition
from agent.timeparse import IST
from agent.transcript import (CallEvent, Outcome, Speaker, ToolCallRecord, Transcript, Turn,
                              mask_phone)
from tools import TOOL_SCHEMAS, TOOLS
from tools.crm import mark_dnc

DEAD_AIR_MS = 4000
MAX_DEAD_AIR_REPROMPTS = 1
MAX_TOOL_ROUNDS = 2
TEXT_MODE_MS_PER_CHAR = 65  # rough TTS speaking rate, used to give text-mode agent turns a duration

_INTENT_OUTCOMES = {
    Intent.APPLY_NOW: Outcome.APPLIED,
    Intent.WRONG_PERSON: Outcome.WRONG_PERSON,
    Intent.NOT_INTERESTED: Outcome.NOT_INTERESTED,
    Intent.DO_NOT_CALL: Outcome.DO_NOT_CALL,
}


@dataclass
class AgentReply:
    text: str
    stage: Stage
    lang: str
    ended: bool


def _cut_at_word(text: str, n: int) -> str:
    if n >= len(text):
        return text
    cut = text[:max(n, 0)]
    if not text[n].isspace():
        cut = cut.rsplit(" ", 1)[0] if " " in cut else ""
    return cut.rstrip()


class CallSession:
    def __init__(self, phone: str, llm: LLM, *, mode: str = "text", call_id: str | None = None,
                 clock: Callable[[], int] | None = None, now_fn: Callable[[], datetime] | None = None):
        t0 = time.monotonic()
        self.phone, self.llm, self.mode = phone, llm, mode
        self.clock = clock or (lambda: int((time.monotonic() - t0) * 1000))
        self.now_fn = now_fn or (lambda: datetime.now(IST))
        self.stage = Stage.GREETING
        self.slots = Slots()
        self.pending: dict[str, int] = {}  # amounts awaiting read-back confirmation
        self.lang = "en"
        self.customer: dict = {}
        self.last_intent: Intent | None = None
        self.history: list[dict[str, str]] = []
        self.last_prompt = ""  # last non-recovery agent line, repeated after recoveries
        self.dead_air_strikes = 0
        self.ended = False
        self.transcript = Transcript(
            call_id=call_id or uuid.uuid4().hex[:12], prompt_version=prompt_version(), mode=mode,
            started_at=self.now_fn(), customer_phone=mask_phone(phone), lang_initial="en",
            stack={"llm": getattr(llm, "name", type(llm).__name__)},
        )

    # ---------------------------------------------------------------- public API
    def start(self) -> AgentReply:
        record = self._run_tool(ToolCall(name="crm_lookup", arguments={"phone": self.phone}))
        self.customer = record.result or {}
        if not self.customer.get("found") or self.customer.get("dnc"):
            reason = "dnc" if self.customer.get("dnc") else "unknown_customer"
            self._event("call_blocked", reason=reason)
            self._finish(Outcome.DO_NOT_CALL if reason == "dnc" else Outcome.DROPPED)
            return AgentReply("", self.stage, self.lang, True)
        self.lang = self.customer.get("preferred_lang", "en")
        self.transcript.lang_initial = self.lang
        return self._say(self._step("enter").reply_text)

    def handle_user(self, text: str, start_ms: int | None = None, end_ms: int | None = None) -> AgentReply:
        if self.ended:
            raise RuntimeError("call has ended")
        text = text.strip()
        self.dead_air_strikes = 0
        lang = detect_lang(text)
        if lang == "en" and self.lang != "en" and len(text.split()) < 3:
            lang = None  # "ok sure" from a Hinglish speaker is not a switch to English
        if lang:
            if lang != self.lang:
                self._event("language_switch", **{"from": self.lang, "to": lang})
            self.lang = lang
        now = self.clock()
        self._add_turn(Speaker.USER, text, start_ms if start_ms is not None else now,
                       end_ms if end_ms is not None else now)

        if is_do_not_call(text):
            mark_dnc(self.phone)
            return self._end_now(Outcome.DO_NOT_CALL, "dnc_goodbye", Intent.DO_NOT_CALL)
        if is_not_interested(text):
            return self._end_now(Outcome.NOT_INTERESTED, "not_interested_goodbye", Intent.NOT_INTERESTED)
        if is_bot_question(text):
            self._event("guardrail", rule="bot_disclosure")
            return self._say(f"{render('bot_disclosure', self.lang)} {self.last_prompt}".strip(),
                             Intent.ASK_IF_BOT, recovery=True)

        if self.pending:
            key, value = next(iter(self.pending.items()))
            if is_affirm(text) and parse_amount(text) in (None, value):
                del self.pending[key]
                setattr(self.slots, key, value)
                self._event("slot_confirmed", slot=key, value=value)
                return self._readback() if self.pending else self._apply(self._step("resume"))
            self.pending.clear()
            self._event("slot_rejected", slot=key, value=value)
            if is_deny(text) and parse_amount(text) is None:
                return self._say(render("ask_amount_again", self.lang), Intent.DENY, recovery=True)
            # otherwise treat it as a fresh answer, e.g. "no, four lakh"

        return self._apply(self._step("user", text))

    def handle_silence(self, duration_ms: int) -> AgentReply | None:
        """Call when the line has been silent for `duration_ms` after the agent finished speaking."""
        if self.ended or duration_ms < DEAD_AIR_MS:
            return None
        self.dead_air_strikes += 1
        self._event("dead_air", duration_ms=duration_ms, strike=self.dead_air_strikes)
        if self.dead_air_strikes <= MAX_DEAD_AIR_REPROMPTS:
            return self._say(f"{render('dead_air_reprompt', self.lang)} {self.last_prompt}".strip(), recovery=True)
        self.stage = Stage.CLOSING
        self._finish(Outcome.NO_RESPONSE)
        return self._say(render("dead_air_goodbye", self.lang), recovery=True)

    def handle_barge_in(self, heard_chars: int, at_ms: int | None = None) -> None:
        """User started speaking while the agent was talking: keep only the text actually played."""
        turns = self.transcript.turns
        if not turns or turns[-1].speaker != Speaker.AGENT or turns[-1].interrupted:
            return
        turn = turns[-1]
        spoken = _cut_at_word(turn.text, heard_chars)
        turn.unspoken_text = turn.text[len(spoken):].strip() or None
        turn.text, turn.interrupted = spoken, True
        turn.end_ms = at_ms if at_ms is not None else self.clock()
        for msg in reversed(self.history):
            if msg["role"] == "assistant":
                msg["content"] = spoken
                break
        self._event("barge_in", heard_chars=heard_chars, discarded=turn.unspoken_text)

    def hang_up(self) -> None:
        if not self.ended:
            self._finish(Outcome.DROPPED)

    # ---------------------------------------------------------------- internals
    def _apply(self, out: LLMTurnOutput) -> AgentReply:
        intent = out.detected_intent
        self.last_intent = intent
        self._merge_slots(out.extracted_slots)
        if self.pending:
            return self._readback(intent)

        reply = out.reply_text.strip()
        target = out.next_stage_suggestion
        if reason := check_transition(self.stage, target, self.slots):
            self._event("transition_rejected", to=target.value, reason=reason)
            target = self.stage
        if target != self.stage:
            self._event("transition", **{"from": self.stage.value, "to": target.value})
            self.stage = target
            reply = f"{reply} {self._step('enter').reply_text}".strip()
        if self.stage == Stage.CLOSING:
            self._finish(self._outcome_for(intent))
        return self._say(reply or render("sorry_repeat", self.lang), intent)

    def _step(self, event: str, user_text: str | None = None) -> LLMTurnOutput:
        results: list[ToolCallRecord] = []
        for round_ in range(MAX_TOOL_ROUNDS + 1):
            try:
                out = self.llm.generate(self._request(event, user_text, results))
            except Exception as e:  # never let a model failure kill the call
                self._event("llm_error", error=f"{type(e).__name__}: {e}")
                return LLMTurnOutput(reply_text=render("sorry_repeat", self.lang), next_stage_suggestion=self.stage)
            if not out.tool_calls or round_ == MAX_TOOL_ROUNDS:
                return out.model_copy(update={"tool_calls": []})
            results += [self._run_tool(call) for call in out.tool_calls]
        raise AssertionError("unreachable")

    def _request(self, event: str, user_text: str | None, results: list[ToolCallRecord]) -> LLMRequest:
        allowed_tools = sorted(STAGE_TOOLS[self.stage])
        allowed_next = sorted(TRANSITIONS[self.stage], key=lambda s: list(Stage).index(s))
        state = {
            "stage": self.stage.value, "lang": self.lang, "now": self.now_fn().isoformat(),
            "customer": {k: self.customer.get(k) for k in
                         ("name", "pre_approved_amount", "offer_rate", "default_tenure")},
            "slots": self.slots.model_dump(), "last_intent": self.last_intent,
            "allowed_next": [s.value for s in allowed_next],
        }
        return LLMRequest(
            stage=self.stage, event=event, user_text=user_text, lang=self.lang, slots=self.slots.model_copy(),
            customer=self.customer, last_intent=self.last_intent, history=list(self.history),
            tool_results=list(results), allowed_tools=allowed_tools, allowed_next=allowed_next,
            system_prompt=build_system_prompt(self.stage, state, [TOOL_SCHEMAS[t] for t in allowed_tools]),
            now=self.now_fn(),
        )

    def _run_tool(self, call: ToolCall) -> ToolCallRecord:
        args, result, error = dict(call.arguments), None, None
        if call.name not in STAGE_TOOLS[self.stage]:
            error = f"tool '{call.name}' not allowed in stage '{self.stage.value}'"
        elif call.name not in TOOLS:
            error = f"unknown tool '{call.name}'"
        else:
            if call.name == "book_callback":  # server-side context the model never supplies
                args.setdefault("phone", self.phone)
                args.setdefault("now", self.now_fn().isoformat())
            try:
                result = TOOLS[call.name](**args)
            except Exception as e:
                error = f"{type(e).__name__}: {e}"
        record = ToolCallRecord(name=call.name, arguments=call.arguments, result=result, error=error,
                                stage=self.stage, turn_index=max(len(self.transcript.turns) - 1, 0),
                                ts_ms=self.clock())
        self.transcript.tool_calls.append(record)
        return record

    def _merge_slots(self, extracted: Slots) -> None:
        for key, value in extracted.model_dump(exclude_none=True).items():
            if key in AMOUNT_SLOTS and value != 0 and value != getattr(self.slots, key):
                self.pending[key] = value
            else:
                setattr(self.slots, key, value)

    def _readback(self, intent: Intent | None = None) -> AgentReply:
        _, value = next(iter(self.pending.items()))
        return self._say(render("readback", self.lang, amount=rupees_words(value, self.lang)), intent)

    def _outcome_for(self, intent: Intent) -> Outcome:
        if intent in _INTENT_OUTCOMES:
            return _INTENT_OUTCOMES[intent]
        booked = any(r.name == "book_callback" and r.result and r.result.get("booked")
                     for r in self.transcript.tool_calls)
        return Outcome.CALLBACK_BOOKED if booked else Outcome.NO_SALE

    def _end_now(self, outcome: Outcome, line: str, intent: Intent) -> AgentReply:
        self._event("guardrail", rule=outcome.value)
        self.stage = Stage.CLOSING
        self._finish(outcome)
        return self._say(render(line, self.lang), intent)

    def _finish(self, outcome: Outcome) -> None:
        self.ended = True
        self.transcript.outcome = outcome
        self.transcript.ended_at = self.now_fn()
        self.transcript.final_slots = self.slots.model_dump(exclude_none=True)

    def _say(self, text: str, intent: Intent | None = None, recovery: bool = False) -> AgentReply:
        start = self.clock()
        duration = len(text) * TEXT_MODE_MS_PER_CHAR if self.mode == "text" else 0
        self._add_turn(Speaker.AGENT, text, start, start + duration, intent)
        self.history.append({"role": "assistant", "content": text})
        if not recovery:
            self.last_prompt = text
        return AgentReply(text, self.stage, self.lang, self.ended)

    def _add_turn(self, speaker: Speaker, text: str, start_ms: int, end_ms: int,
                  intent: Intent | None = None) -> None:
        if speaker == Speaker.USER:
            self.history.append({"role": "user", "content": text})
        self.transcript.turns.append(Turn(
            index=len(self.transcript.turns), speaker=speaker, text=text, lang=self.lang,
            start_ms=start_ms, end_ms=end_ms, stage=self.stage, intent=intent.value if intent else None,
        ))

    def _event(self, type_: str, **detail) -> None:
        self.transcript.events.append(CallEvent(type=type_, ts_ms=self.clock(), stage=self.stage, detail=detail))
