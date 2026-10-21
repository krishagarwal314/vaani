"""Mock callback scheduler. Calls are only allowed 09:00-21:00 IST."""
from __future__ import annotations

import uuid
from datetime import datetime

from agent.timeparse import IST

CALL_WINDOW = (9, 21)
CALLBACKS: list[dict] = []


def book_callback(time: str, phone: str | None = None, now: str | None = None) -> dict:
    when = datetime.fromisoformat(time)
    if when.tzinfo is None:
        when = when.replace(tzinfo=IST)
    current = datetime.fromisoformat(now) if now else datetime.now(IST)
    local = when.astimezone(IST)
    if when <= current:
        return {"booked": False, "error": "time_in_past"}
    if not CALL_WINDOW[0] <= local.hour < CALL_WINDOW[1]:
        return {"booked": False, "error": "outside_call_window"}
    booking = {"booked": True, "callback_id": uuid.uuid4().hex[:8], "time": local.isoformat(), "phone": phone}
    CALLBACKS.append(booking)
    return booking
