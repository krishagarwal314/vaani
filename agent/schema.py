"""Structured LLM I/O. The LLM must return `LLMTurnOutput`; the engine validates everything."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from agent.stages import Stage
from agent.transcript import Lang, ToolCallRecord


class Intent(str, Enum):
    AFFIRM = "affirm"
    DENY = "deny"
    PROVIDE_INFO = "provide_info"
    ASK_QUESTION = "ask_question"
    APPLY_NOW = "apply_now"
    REQUEST_CALLBACK = "request_callback"
    OBJECTION_RATE = "objection_rate"
    OBJECTION_EXISTING_LOAN = "objection_existing_loan"
    OBJECTION_FAMILY = "objection_family"
    OBJECTION_TRUST = "objection_trust"
    OBJECTION_BAD_TIME = "objection_bad_time"
    OFF_TOPIC = "off_topic"
    ASK_IF_BOT = "ask_if_bot"
    WRONG_PERSON = "wrong_person"
    NOT_INTERESTED = "not_interested"
    DO_NOT_CALL = "do_not_call"
    OTHER = "other"


OBJECTION_INTENTS = {
    Intent.OBJECTION_RATE, Intent.OBJECTION_EXISTING_LOAN,
    Intent.OBJECTION_FAMILY, Intent.OBJECTION_TRUST,
}


class Slots(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identity_confirmed: bool | None = None
    consent_given: bool | None = None
    loan_amount: int | None = None          # INR
    loan_purpose: str | None = None
    employment_type: Literal["salaried", "self_employed"] | None = None
    monthly_income: int | None = None       # INR, take-home
    existing_emi: int | None = None         # INR per month, 0 = none
    tenure_months: int | None = None
    callback_time: str | None = None        # ISO 8601 with offset


# Amounts are always read back to the caller before they are accepted into the call state.
AMOUNT_SLOTS = ("loan_amount", "monthly_income", "existing_emi")


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = {}


class LLMTurnOutput(BaseModel):
    reply_text: str = ""
    detected_intent: Intent = Intent.OTHER
    extracted_slots: Slots = Slots()
    next_stage_suggestion: Stage
    tool_calls: list[ToolCall] = []


class LLMRequest(BaseModel):
    """Everything an LLM backend needs for one step.

    event: "enter" = speak the opening line of a stage just entered,
           "user"  = respond to the latest user turn (already in history),
           "resume" = the caller just confirmed a read-back amount; continue the stage.
    """
    stage: Stage
    event: Literal["enter", "user", "resume"]
    user_text: str | None = None
    lang: Lang
    slots: Slots
    customer: dict[str, Any]
    last_intent: Intent | None = None
    history: list[dict[str, str]]
    tool_results: list[ToolCallRecord] = []
    allowed_tools: list[str]
    allowed_next: list[Stage]
    system_prompt: str
    now: datetime
