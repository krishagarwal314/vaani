"""Indian-system amount parsing ("5 lakh", "paanch lakh", "50,000", "1.2 cr") and read-back words."""
from __future__ import annotations

import re

_WORD_NUM = {
    "one": 1, "ek": 1, "two": 2, "do": 2, "three": 3, "teen": 3, "four": 4, "char": 4, "chaar": 4,
    "five": 5, "paanch": 5, "panch": 5, "six": 6, "chhe": 6, "seven": 7, "saat": 7, "eight": 8,
    "aath": 8, "nine": 9, "nau": 9, "ten": 10, "das": 10, "fifteen": 15, "pandrah": 15, "twenty": 20,
    "bees": 20, "twenty-five": 25, "pachees": 25, "thirty": 30, "tees": 30, "forty": 40, "chalis": 40,
    "fifty": 50, "pachaas": 50, "pachas": 50, "dedh": 1.5, "dhai": 2.5, "half": 0.5,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "दस": 10, "बीस": 20, "पचास": 50,
}
_MULT = {
    "lakh": 10**5, "lakhs": 10**5, "lac": 10**5, "lacs": 10**5, "l": 10**5, "लाख": 10**5,
    "crore": 10**7, "crores": 10**7, "cr": 10**7, "करोड़": 10**7,
    "k": 10**3, "thousand": 10**3, "hazaar": 10**3, "hazar": 10**3, "hajar": 10**3, "हज़ार": 10**3, "हजार": 10**3,
}
_NUM = re.compile(r"^\d+(?:\.\d+)?$")
_GLUED = re.compile(r"^(\d+(?:\.\d+)?)(lakhs?|lacs?|l|k|cr|crores?)$")
_SPLIT = re.compile(r"[\s!?।;:()\"]+")


def parse_amount(text: str) -> int | None:
    """First money amount in `text`, in rupees. Bare numbers under 1000 (tenures, rates) are ignored."""
    text = re.sub(r"(?<=\d),(?=\d)", "", text.lower().replace("₹", " ").replace("rs.", " "))
    tokens = [t.strip(".,'") for t in _SPLIT.split(text) if t.strip(".,'")]
    for i, tok in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        if nxt == "%" or nxt.startswith("percent"):
            continue
        if m := _GLUED.match(tok):
            return int(float(m.group(1)) * _MULT[m.group(2)])
        if _NUM.match(tok):
            value = float(tok)
        elif tok in _WORD_NUM and nxt in _MULT:
            value = _WORD_NUM[tok]
        else:
            continue
        if nxt in _MULT:
            return int(value * _MULT[nxt])
        if value >= 1000:
            return int(value)
    return None


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
         "fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _below_1000(n: int) -> str:
    parts = []
    if n >= 100:
        parts.append(f"{_ONES[n // 100]} hundred")
        n %= 100
    if n >= 20:
        parts.append(_TENS[n // 10] + (f"-{_ONES[n % 10]}" if n % 10 else ""))
    elif n or not parts:
        parts.append(_ONES[n])
    return " ".join(parts)


def number_words(n: int) -> str:
    """Indian numbering system: 1250000 -> 'twelve lakh fifty thousand'."""
    if n < 1000:
        return _below_1000(n)
    parts = []
    for unit, size in (("crore", 10**7), ("lakh", 10**5), ("thousand", 10**3)):
        if n >= size:
            parts.append(f"{number_words(n // size)} {unit}")
            n %= size
    if n:
        parts.append(_below_1000(n))
    return " ".join(parts)


def rupees_words(n: int | float, lang: str = "en") -> str:
    return f"{number_words(round(n))} {'rupaye' if lang == 'hinglish' else 'rupees'}"
