"""Short backchannel fillers, played only when the LLM is slow to produce its first token."""
from __future__ import annotations

FILLERS = {
    "en": ["Got it.", "Okay.", "Right."],
    "hinglish": ["Haan ji.", "Achha.", "Theek hai."],
    "hi": ["हाँ जी।", "अच्छा।", "ठीक है।"],
}


class FillerPolicy:
    def __init__(self, threshold_ms: int = 700):
        self.threshold_ms = threshold_ms
        self._i = 0

    def pick(self, waited_ms: int, lang: str) -> str | None:
        """Return a filler if we've waited past the threshold without a first token, else None."""
        if waited_ms < self.threshold_ms:
            return None
        options = FILLERS.get(lang, FILLERS["en"])
        self._i += 1
        return options[self._i % len(options)]  # rotate so the same filler isn't repeated back to back
