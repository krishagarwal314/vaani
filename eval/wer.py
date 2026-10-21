"""Word error rate, overall and restricted to number/amount words (Phase 4 STT evaluation).

    python eval/wer.py refs.txt hyps.txt     # one utterance per line, aligned
"""
from __future__ import annotations

import re
import sys

_NUMBER_WORDS = set(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand "
    "lakh lakhs crore crores ek do teen char paanch chhe saat aath nau das hazaar".split()
)


def normalize(text: str) -> list[str]:
    return re.sub(r"[^\w\s']", " ", text.lower()).split()


def edit_distance(ref: list[str], hyp: list[str]) -> int:
    prev = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        cur = [i] + [0] * len(hyp)
        for j, h in enumerate(hyp, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (r != h))
        prev = cur
    return prev[-1]


def wer(refs: list[str], hyps: list[str], numbers_only: bool = False) -> float:
    errors = words = 0
    for ref, hyp in zip(refs, hyps, strict=True):
        r, h = normalize(ref), normalize(hyp)
        if numbers_only:
            r = [w for w in r if w.isdigit() or w in _NUMBER_WORDS]
            h = [w for w in h if w.isdigit() or w in _NUMBER_WORDS]
        errors += edit_distance(r, h)
        words += len(r)
    return errors / words if words else 0.0


if __name__ == "__main__":
    refs = open(sys.argv[1]).read().splitlines()
    hyps = open(sys.argv[2]).read().splitlines()
    print(f"WER: {wer(refs, hyps):.3f}   number WER: {wer(refs, hyps, numbers_only=True):.3f}")
