"""The 9-stage call state machine: stages, allowed transitions, per-stage tools and guards.

The LLM only *suggests* a next stage. `check_transition` is the single authority on whether
the call actually moves.
"""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.schema import Slots


class Stage(str, Enum):
    GREETING = "greeting"              # 1 greeting & identity confirmation
    CONSENT = "consent"                # 2 consent / purpose disclosure
    NEED_DISCOVERY = "need_discovery"  # 3
    ELIGIBILITY = "eligibility"        # 4 income, employment type, existing EMIs
    OFFER = "offer"                    # 5 offer & EMI quote
    OBJECTION = "objection"            # 6
    COMMITMENT = "commitment"          # 7 apply now or book callback
    CALLBACK = "callback"              # 8 callback scheduling
    CLOSING = "closing"                # 9


S = Stage

# Callback and closing are reachable from every live stage (bad time, not interested, ...).
_EXITS = {S.CALLBACK, S.CLOSING}

TRANSITIONS: dict[Stage, frozenset[Stage]] = {
    S.GREETING: frozenset({S.CONSENT} | _EXITS),
    S.CONSENT: frozenset({S.NEED_DISCOVERY} | _EXITS),
    S.NEED_DISCOVERY: frozenset({S.ELIGIBILITY, S.OBJECTION} | _EXITS),
    S.ELIGIBILITY: frozenset({S.OFFER, S.OBJECTION} | _EXITS),
    S.OFFER: frozenset({S.OBJECTION, S.COMMITMENT} | _EXITS),
    S.OBJECTION: frozenset({S.OFFER, S.COMMITMENT} | _EXITS),
    S.COMMITMENT: frozenset({S.OBJECTION} | _EXITS),
    S.CALLBACK: frozenset({S.CLOSING}),
    S.CLOSING: frozenset(),
}

STAGE_TOOLS: dict[Stage, frozenset[str]] = {
    S.GREETING: frozenset({"crm_lookup"}),
    S.CONSENT: frozenset(),
    S.NEED_DISCOVERY: frozenset(),
    S.ELIGIBILITY: frozenset(),
    S.OFFER: frozenset({"calculate_emi"}),
    S.OBJECTION: frozenset({"calculate_emi"}),
    S.COMMITMENT: frozenset(),
    S.CALLBACK: frozenset({"book_callback"}),
    S.CLOSING: frozenset(),
}

ELIGIBILITY_SLOTS = ("employment_type", "monthly_income", "existing_emi")


def check_transition(current: Stage, target: Stage, slots: "Slots") -> str | None:
    """Return None if `current -> target` is allowed, else a human-readable rejection reason."""
    if target == current:
        return None
    if target not in TRANSITIONS[current]:
        return f"{current.value} -> {target.value} is not an allowed transition"
    if target == S.NEED_DISCOVERY and not slots.consent_given:
        return "consent not given"
    if target == S.ELIGIBILITY and slots.loan_amount is None:
        return "loan_amount not confirmed"
    if target == S.OFFER:
        missing = [s for s in ("loan_amount", *ELIGIBILITY_SLOTS) if getattr(slots, s) is None]
        if missing:
            return f"missing slots: {', '.join(missing)}"
    return None
