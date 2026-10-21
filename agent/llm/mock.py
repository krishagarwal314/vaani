"""Deterministic keyword-based stand-in for the LLM.

Lets the CLI and the test suite run the full 9-stage flow offline, and documents the behaviour the
real model is prompted to produce. It is intentionally simple; it is not the product.
"""
from __future__ import annotations

from agent.lang import is_affirm, is_deny
from agent.numbers import parse_amount, rupees_words
from agent.responses import render
from agent.schema import Intent, LLMRequest, LLMTurnOutput, Slots, ToolCall
from agent.stages import ELIGIBILITY_SLOTS, Stage
from agent.timeparse import describe_time, parse_callback_time

I = Intent
_KEYWORDS: list[tuple[Intent, tuple[str, ...]]] = [
    (I.OBJECTION_BAD_TIME, ("busy", "later", "baad mein", "abhi nahi", "not now", "driving", "meeting",
                            "call back", "callback", "call me")),
    (I.OBJECTION_RATE, ("interest rate", "rate", "too high", "expensive", "mehenga", "mehnga", "byaaj", "byaj")),
    (I.OBJECTION_EXISTING_LOAN, ("already have", "existing loan", "already a loan", "pehle se", "chal raha",
                                 "another loan")),
    (I.OBJECTION_FAMILY, ("family", "wife", "husband", "ghar wal", "parents", "discuss", "puchna", "poochna",
                          "ask my")),
    (I.OBJECTION_TRUST, ("trust", "fraud", "scam", "bharosa", "fake", "genuine")),
    (I.APPLY_NOW, ("apply", "proceed", "go ahead", "kar do", "aage badh", "link bhej", "send the link")),
    (I.OFF_TOPIC, ("cricket", "weather", "mausam", "match", "movie", "politics", "ipl")),
]
_PURPOSES = {
    "wedding": ("wedding", "shaadi", "marriage"), "medical": ("medical", "hospital", "treatment", "ilaaj"),
    "home_renovation": ("renovation", "repair", "ghar ka kaam"), "education": ("education", "fees", "padhai"),
    "travel": ("travel", "trip", "ghoomne"), "business": ("business", "dukaan", "shop"),
}
_SALARIED = ("salaried", "salary", "job", "naukri", "employee", "company mein", "नौकरी")
_SELF_EMPLOYED = ("self", "business", "khud ka", "apna kaam", "dukaan", "freelance", "अपना")


def classify(text: str) -> Intent | None:
    t = text.lower()
    for intent, words in _KEYWORDS:
        if any(w in t for w in words):
            return intent
    return None


def _out(req: LLMRequest, reply: str = "", intent: Intent = I.OTHER, next_stage: Stage | None = None,
         tools: list[ToolCall] | None = None, **slots) -> LLMTurnOutput:
    return LLMTurnOutput(reply_text=reply, detected_intent=intent, extracted_slots=Slots(**slots),
                         next_stage_suggestion=next_stage or req.stage, tool_calls=tools or [])


class MockLLM:
    name = "mock"

    def generate(self, req: LLMRequest) -> LLMTurnOutput:
        return getattr(self, f"_{req.stage.value}")(req)

    # helpers ---------------------------------------------------------------------------------
    def _steer(self, req: LLMRequest, question: str) -> LLMTurnOutput:
        return _out(req, f"{render('off_topic', req.lang)} {question}", I.OFF_TOPIC)

    def _route_common(self, req: LLMRequest, intent: Intent | None) -> LLMTurnOutput | None:
        if intent == I.OBJECTION_BAD_TIME:
            return _out(req, intent=intent, next_stage=Stage.CALLBACK)
        if intent in (I.OBJECTION_RATE, I.OBJECTION_EXISTING_LOAN, I.OBJECTION_FAMILY, I.OBJECTION_TRUST):
            return _out(req, intent=intent, next_stage=Stage.OBJECTION)
        return None

    # stages ----------------------------------------------------------------------------------
    def _greeting(self, req):
        question = render("greeting", req.lang, name=req.customer.get("name", ""))
        if req.event != "user":
            return _out(req, question)
        if classify(req.user_text) == I.OBJECTION_BAD_TIME:
            return _out(req, intent=I.OBJECTION_BAD_TIME, next_stage=Stage.CALLBACK, identity_confirmed=True)
        if is_deny(req.user_text):
            return _out(req, intent=I.WRONG_PERSON, next_stage=Stage.CLOSING, identity_confirmed=False)
        if is_affirm(req.user_text):
            return _out(req, intent=I.AFFIRM, next_stage=Stage.CONSENT, identity_confirmed=True)
        return self._steer(req, question)

    def _consent(self, req):
        first = req.customer.get("name", "").split(" ")[0]
        if req.event != "user":
            return _out(req, render("consent", req.lang, name=first))
        if classify(req.user_text) == I.OBJECTION_BAD_TIME:
            return _out(req, intent=I.OBJECTION_BAD_TIME, next_stage=Stage.CALLBACK)
        if is_deny(req.user_text):
            return _out(req, intent=I.NOT_INTERESTED, next_stage=Stage.CLOSING, consent_given=False)
        if is_affirm(req.user_text):
            return _out(req, intent=I.AFFIRM, next_stage=Stage.NEED_DISCOVERY, consent_given=True)
        return self._steer(req, render("consent", req.lang, name=first))

    def _need_discovery(self, req):
        question = render("need_discovery", req.lang)
        if req.event == "enter":
            return _out(req, question)
        if req.event == "resume":
            return _out(req, next_stage=Stage.ELIGIBILITY if req.slots.loan_amount else None)
        t = req.user_text.lower()
        if routed := self._route_common(req, classify(t)):
            return routed
        amount = parse_amount(t)
        purpose = next((p for p, words in _PURPOSES.items() if any(w in t for w in words)), None)
        if amount:
            return _out(req, intent=I.PROVIDE_INFO, next_stage=Stage.ELIGIBILITY,
                        loan_amount=amount, loan_purpose=purpose)
        if purpose:
            return _out(req, question, I.PROVIDE_INFO, loan_purpose=purpose)
        return self._steer(req, question)

    def _eligibility(self, req):
        def first_missing(slots: dict) -> str | None:
            return next((s for s in ELIGIBILITY_SLOTS if slots.get(s) is None), None)

        current = req.slots.model_dump()
        missing = first_missing(current)
        if req.event != "user":
            if missing is None:
                return _out(req, next_stage=Stage.OFFER)
            return _out(req, render(f"ask_{missing}", req.lang))

        t = req.user_text.lower()
        if routed := self._route_common(req, classify(t)):
            return routed
        found: dict = {}
        if missing == "employment_type" or any(w in t for w in _SALARIED + _SELF_EMPLOYED):
            if any(w in t for w in _SELF_EMPLOYED):
                found["employment_type"] = "self_employed"
            elif any(w in t for w in _SALARIED):
                found["employment_type"] = "salaried"
        amount = parse_amount(t)
        if missing == "monthly_income" and amount:
            found["monthly_income"] = amount
        elif missing == "existing_emi":
            if amount:
                found["existing_emi"] = amount
            elif is_deny(t) or any(w in t for w in ("none", "zero", "koi nahi", "koi emi nahi")):
                found["existing_emi"] = 0
        if not found:
            return self._steer(req, render(f"ask_{missing}", req.lang))
        after = first_missing({**current, **found})
        if after is None:
            return _out(req, intent=I.PROVIDE_INFO, next_stage=Stage.OFFER, **found)
        return _out(req, render(f"ask_{after}", req.lang), I.PROVIDE_INFO, **found)

    def _quote(self, req) -> LLMTurnOutput:
        emi = next((r for r in reversed(req.tool_results) if r.name == "calculate_emi" and r.result), None)
        if emi is None:
            principal = min(req.slots.loan_amount or 0, req.customer.get("pre_approved_amount") or 0)
            tenure = req.slots.tenure_months or req.customer.get("default_tenure", 36)
            return _out(req, tools=[ToolCall(name="calculate_emi", arguments={
                "principal": principal, "rate": req.customer.get("offer_rate", 12.0), "tenure": tenure})])
        r = emi.result
        return _out(req, render("offer", req.lang, amount=rupees_words(r["principal"], req.lang),
                                rate=f"{r['rate']:g}", tenure=r["tenure"], emi=rupees_words(r["emi"], req.lang)))

    def _offer(self, req):
        if req.event != "user":
            return self._quote(req)
        t = req.user_text
        intent = classify(t)
        if routed := self._route_common(req, intent):
            return routed
        if intent == I.APPLY_NOW or is_affirm(t):
            return _out(req, intent=I.AFFIRM, next_stage=Stage.COMMITMENT)
        if is_deny(t):
            return _out(req, intent=I.DENY, next_stage=Stage.OBJECTION)
        return self._steer(req, render("offer_confirm", req.lang))

    def _objection(self, req):
        def strategy(intent: Intent | None) -> str:
            key = intent.value if intent and intent.value.startswith("objection_") else "objection_generic"
            return render(key if key != "objection_bad_time" else "objection_generic", req.lang)

        if req.event != "user":
            return _out(req, strategy(req.last_intent))
        t = req.user_text
        intent = classify(t)
        if intent == I.OBJECTION_BAD_TIME:
            return _out(req, intent=intent, next_stage=Stage.CALLBACK)
        if intent and intent.value.startswith("objection_"):
            return _out(req, strategy(intent), intent)
        if is_affirm(t) or intent == I.APPLY_NOW:
            if req.last_intent == I.OBJECTION_FAMILY:
                return _out(req, intent=I.REQUEST_CALLBACK, next_stage=Stage.CALLBACK)
            return _out(req, intent=I.AFFIRM, next_stage=Stage.COMMITMENT)
        if is_deny(t):
            return _out(req, intent=I.NOT_INTERESTED, next_stage=Stage.CLOSING)
        return self._steer(req, strategy(None))

    def _commitment(self, req):
        if req.event != "user":
            return _out(req, render("commitment", req.lang))
        t = req.user_text
        intent = classify(t)
        if intent == I.OBJECTION_BAD_TIME or is_deny(t):
            return _out(req, intent=I.REQUEST_CALLBACK, next_stage=Stage.CALLBACK)
        if routed := self._route_common(req, intent):
            return routed
        if intent == I.APPLY_NOW or is_affirm(t):
            return _out(req, render("applied", req.lang), I.APPLY_NOW, Stage.CLOSING)
        return self._steer(req, render("commitment", req.lang))

    def _callback(self, req):
        if req.event != "user":
            return _out(req, render("callback_ask", req.lang))
        booking = next((r for r in reversed(req.tool_results) if r.name == "book_callback"), None)
        if booking is not None:
            result = booking.result or {}
            if result.get("booked"):
                from datetime import datetime
                when = datetime.fromisoformat(result["time"])
                return _out(req, render("callback_booked", req.lang, when=describe_time(when, req.now)),
                            I.PROVIDE_INFO, Stage.CLOSING, callback_time=result["time"])
            key = "callback_bad_time" if result.get("error") == "outside_call_window" else "callback_unclear"
            return _out(req, render(key, req.lang), I.PROVIDE_INFO)
        when = parse_callback_time(req.user_text, req.now)
        if when is None:
            return _out(req, render("callback_unclear", req.lang), I.OTHER)
        return _out(req, tools=[ToolCall(name="book_callback", arguments={"time": when.isoformat()})])

    def _closing(self, req):
        if req.last_intent == I.WRONG_PERSON:
            return _out(req, render("closing_wrong_person", req.lang))
        first = req.customer.get("name", "").split(" ")[0]
        return _out(req, render("closing", req.lang, name=first))
