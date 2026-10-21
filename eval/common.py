from __future__ import annotations

import math
from pathlib import Path

from agent.transcript import Transcript


def load_transcripts(directory: str | Path) -> list[Transcript]:
    return [Transcript.load(p) for p in sorted(Path(directory).glob("*.json"))]


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (p in 0-100)."""
    if not values:
        return math.nan
    ordered = sorted(values)
    return ordered[max(math.ceil(p / 100 * len(ordered)) - 1, 0)]
