"""Deterministic checks that run before the LLM: do-not-call, not interested, "are you a bot?".

These must never depend on model behaviour, so they are plain pattern matches.
"""
from __future__ import annotations

import re

_DNC = re.compile(
    r"(do\s*n[o']?t\s+call|stop\s+calling|never\s+call|remove\s+my\s+number|call\s+mat\s+kar|"
    r"phone\s+mat\s+kar|dobara\s+(call|phone)\s+mat|कॉल\s+मत|फोन\s+मत)", re.I)
_NOT_INTERESTED = re.compile(
    r"(not\s+interested|no\s+interest|interested\s+nahi|interest\s+nahi|nahi\s+chahiye|nahin\s+chahiye|"
    r"don'?t\s+(want|need)\s+(a\s+|any\s+|the\s+)?loan|loan\s+nahi\s+chahiye|ज़रूरत\s+नहीं|नहीं\s+चाहिए)", re.I)
_BOT = re.compile(
    r"(are\s+you\s+(a\s+)?(bot|robot|machine|ai|human|real)|is\s+this\s+(a\s+)?(bot|recording|robot)|"
    r"real\s+person|(robot|bot|machine|computer|ai)\s+(ho|hai|hain)|insaan\s+ho|kya\s+(aap|tum)\s+(robot|bot)|"
    r"रोबोट)", re.I)


def is_do_not_call(text: str) -> bool:
    return bool(_DNC.search(text))


def is_not_interested(text: str) -> bool:
    return bool(_NOT_INTERESTED.search(text))


def is_bot_question(text: str) -> bool:
    return bool(_BOT.search(text))
