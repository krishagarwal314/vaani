"""Talk-over rate per turn-detection mode.

    python eval/talk_over.py transcripts/

A user turn is "talked over" when the agent's first audio byte comes before the ground-truth end of
the user's speech (user_true_end_ms, annotated by the test harness).
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.common import load_transcripts  # noqa: E402


def talk_over_rates(transcripts) -> dict[str, tuple[int, int]]:
    """detector -> (talked_over, total) over agent turns with both marks."""
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for t in transcripts:
        for turn in t.turns:
            m = turn.metrics
            if not m or m.user_true_end_ms is None or m.tts_first_byte_ms is None:
                continue
            c = counts[m.turn_detector or "unknown"]
            c[0] += m.tts_first_byte_ms < m.user_true_end_ms
            c[1] += 1
    return {k: (v[0], v[1]) for k, v in counts.items()}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default="transcripts")
    rates = talk_over_rates(load_transcripts(parser.parse_args().directory))
    if not rates:
        sys.exit("no annotated voice turns found (Phase 3 harness not run yet)")
    for detector, (over, total) in sorted(rates.items()):
        print(f"{detector:<10} {over}/{total} = {100 * over / total:.1f}%")


if __name__ == "__main__":
    main()
