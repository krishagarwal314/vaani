"""Split streaming LLM tokens into sentences so TTS can start before the full reply exists."""
from __future__ import annotations

import re

_ABBREV = ("mr.", "mrs.", "ms.", "dr.", "rs.", "no.", "approx.", "etc.")
_END = re.compile(r"[.?!।](?=\s)")


class SentenceChunker:
    def __init__(self, min_chars: int = 12):
        self.min_chars = min_chars
        self._buf = ""

    def feed(self, token: str) -> list[str]:
        self._buf += token
        out: list[str] = []
        start = 0
        for m in _END.finditer(self._buf):
            candidate = self._buf[start:m.end()].strip()
            if len(candidate) < self.min_chars or candidate.lower().endswith(_ABBREV):
                continue
            out.append(candidate)
            start = m.end()
        self._buf = self._buf[start:]
        return out

    def flush(self) -> list[str]:
        rest, self._buf = self._buf.strip(), ""
        return [rest] if rest else []
