"""Parse spoken callback times ("tomorrow 5pm", "kal shaam 6 baje") into IST datetimes."""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

_TIME = re.compile(r"\b(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.|baje|o'?clock)?")
_EVENING = ("evening", "shaam", "sham", "night", "raat")
_AFTERNOON = ("afternoon", "dopahar", "dopaher", "lunch")
_MORNING = ("morning", "subah")


def parse_callback_time(text: str, now: datetime) -> datetime | None:
    t = text.lower()
    now = now.astimezone(IST)
    if "day after tomorrow" in t or re.search(r"\bparso\b", t):
        days, explicit = 2, True
    elif "tomorrow" in t or re.search(r"\bkal\b", t):
        days, explicit = 1, True
    else:
        days, explicit = 0, "today" in t or re.search(r"\baaj\b", t) is not None

    m = _TIME.search(t)
    if m:
        hour, minute, mer = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").replace(".", "")
        if mer == "pm" and hour < 12:
            hour += 12
        elif mer == "am" and hour == 12:
            hour = 0
        elif mer not in ("am", "pm"):
            if any(w in t for w in _EVENING + _AFTERNOON) and hour < 12:
                hour += 12
            elif not any(w in t for w in _MORNING) and hour < 8:
                hour += 12  # "call at 5" on a sales call means 5 PM
    elif any(w in t for w in _EVENING):
        hour, minute = 18, 0
    elif any(w in t for w in _AFTERNOON):
        hour, minute = 14, 0
    elif any(w in t for w in _MORNING):
        hour, minute = 10, 0
    else:
        return None
    if hour > 23 or minute > 59:
        return None

    when = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days)
    if when <= now and not explicit:
        when += timedelta(days=1)
    return when


def describe_time(when: datetime, now: datetime) -> str:
    when, now = when.astimezone(IST), now.astimezone(IST)
    delta = (when.date() - now.date()).days
    day = {0: "today", 1: "tomorrow"}.get(delta, when.strftime("%d %B").lstrip("0"))
    clock = when.strftime("%I:%M %p").lstrip("0").replace(":00", "")
    return f"{day} at {clock}"
