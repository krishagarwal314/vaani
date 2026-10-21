"""Lightweight language ID for English / Hindi (Devanagari) / romanized Hinglish, plus yes/no."""
from __future__ import annotations

import re

from agent.transcript import Lang

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_TOKEN = re.compile(r"[a-z']+")

HINGLISH_WORDS = {
    "haan", "haanji", "han", "ha", "nahi", "nahin", "nai", "hai", "hain", "kya", "mujhe", "mera", "meri",
    "chahiye", "kal", "aaj", "baje", "aap", "aapka", "kar", "karo", "karna", "ji", "theek", "thik",
    "accha", "acha", "achha", "abhi", "baad", "mein", "main", "ka", "ki", "ke", "ho", "hoon", "hu",
    "toh", "bhi", "kitna", "kitni", "paisa", "rupaye", "lakh", "shaam", "subah", "ghar", "wale", "bolo",
    "batao", "samajh", "zyada", "kam", "mat", "naukri", "kaam", "dena", "lena", "chal", "raha", "rahi",
    "hazaar", "hazar", "se", "walon", "puchna", "poochna", "padega", "hoga", "nahi", "koi", "sahi", "bhai",
}
_NEUTRAL = {"ok", "okay", "hmm", "umm", "hello", "hi", "emi", "loan", "rupees", "lakh", "crore", "k"}

_AFFIRM = {
    "yes", "yeah", "yep", "yup", "sure", "correct", "right", "ok", "okay", "haan", "haanji", "han", "ha",
    "ji", "sahi", "theek", "thik", "bilkul", "zaroor", "absolutely", "speaking", "hai", "go",
}
_AFFIRM_DEV = ("हाँ", "हां", "जी", "सही", "ठीक", "बिल्कुल")
_DENY = {"no", "nope", "nahi", "nahin", "nai", "galat", "wrong", "not"}
_DENY_DEV = ("नहीं", "गलत")


def detect_lang(text: str) -> Lang | None:
    """Return the language of `text`, or None if it carries no signal (e.g. "ok", "5 lakh")."""
    if _DEVANAGARI.search(text):
        return "hi"
    tokens = [t for t in _TOKEN.findall(text.lower()) if t not in _NEUTRAL]
    if not tokens:
        return None
    hinglish = sum(t in HINGLISH_WORDS for t in tokens)
    return "hinglish" if hinglish / len(tokens) >= 0.25 else "en"


def _tokens(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def is_deny(text: str) -> bool:
    return bool(_tokens(text) & _DENY) or any(w in text for w in _DENY_DEV)


def is_affirm(text: str) -> bool:
    return not is_deny(text) and (bool(_tokens(text) & _AFFIRM) or any(w in text for w in _AFFIRM_DEV))
