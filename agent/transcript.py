"""Call transcript format shared by text and voice calls (consumed by CallQC).

All timestamps are integer milliseconds since call start. Regenerate the JSON Schema with
`python -m agent.transcript > schemas/transcript.schema.json`.
"""
from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from agent.stages import Stage

SCHEMA_VERSION = "1.0"

Lang = Literal["en", "hi", "hinglish"]


class Speaker(str, Enum):
    AGENT = "agent"
    USER = "user"


class Outcome(str, Enum):
    IN_PROGRESS = "in_progress"
    APPLIED = "applied"
    CALLBACK_BOOKED = "callback_booked"
    NOT_INTERESTED = "not_interested"
    DO_NOT_CALL = "do_not_call"
    WRONG_PERSON = "wrong_person"
    NO_RESPONSE = "no_response"  # dead air twice
    NO_SALE = "no_sale"          # reached closing without a commitment
    DROPPED = "dropped"          # caller hung up / session ended mid-call


class TurnMetrics(BaseModel):
    """Voice-mode latency marks (ms since call start), attached to agent turns.

    Voice-to-voice latency = tts_first_byte_ms - user_eos_ms. Null in text mode.
    """
    user_eos_ms: int | None = None          # end of user speech as decided by the turn detector
    user_true_end_ms: int | None = None     # ground-truth end of speech (test-harness annotation)
    stt_final_ms: int | None = None
    llm_first_token_ms: int | None = None
    tts_first_byte_ms: int | None = None
    turn_detector: str | None = None        # vad | livekit | custom
    filler_used: str | None = None


class Turn(BaseModel):
    index: int
    speaker: Speaker
    text: str = Field(description="What was actually spoken (agent text is truncated on barge-in)")
    lang: Lang
    start_ms: int
    end_ms: int
    stage: Stage
    intent: str | None = None
    interrupted: bool = False
    unspoken_text: str | None = Field(None, description="Agent text discarded because of barge-in")
    metrics: TurnMetrics | None = None


class ToolCallRecord(BaseModel):
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    stage: Stage
    turn_index: int = Field(description="Index of the turn that triggered the call")
    ts_ms: int


class CallEvent(BaseModel):
    """Non-turn happenings: transitions, rejected transitions, barge-in, dead air, guardrails."""
    type: str
    ts_ms: int
    stage: Stage
    detail: dict[str, Any] = {}


class Transcript(BaseModel):
    schema_version: str = SCHEMA_VERSION
    call_id: str
    prompt_version: str
    mode: Literal["text", "voice"]
    started_at: datetime
    ended_at: datetime | None = None
    customer_phone: str = Field(description="Masked, e.g. +91******0001")
    lang_initial: Lang
    stack: dict[str, str] = Field(default_factory=dict, description="llm / stt / tts / turn_detector")
    turns: list[Turn] = []
    outcome: Outcome = Outcome.IN_PROGRESS
    tool_calls: list[ToolCallRecord] = []
    events: list[CallEvent] = []
    final_slots: dict[str, Any] = {}

    def save(self, directory: str | Path) -> Path:
        path = Path(directory) / f"{self.call_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2))
        return path

    @classmethod
    def load(cls, path: str | Path) -> "Transcript":
        return cls.model_validate_json(Path(path).read_text())


def mask_phone(phone: str) -> str:
    return phone[:3] + "*" * max(len(phone) - 7, 0) + phone[-4:] if len(phone) > 7 else phone


if __name__ == "__main__":
    print(json.dumps(Transcript.model_json_schema(), indent=2))
