"""Pluggable end-of-turn detection (Phase 3 compares all three on the same recorded audio)."""
from __future__ import annotations

import os
from typing import Protocol


class TurnDetector(Protocol):
    name: str

    def is_end_of_turn(self, partial_transcript: str, silence_ms: int) -> bool: ...


class VADSilenceDetector:
    """(a) Baseline: end of turn after a fixed silence once Silero VAD reports no speech."""
    name = "vad"

    def __init__(self, silence_ms: int = 500):
        self.silence_ms = silence_ms

    def is_end_of_turn(self, partial_transcript: str, silence_ms: int) -> bool:
        return silence_ms >= self.silence_ms


class LiveKitTurnDetector:
    """(b) LiveKit's built-in turn-detector model. TODO(phase 3): wrap livekit.plugins.turn_detector."""
    name = "livekit"

    def is_end_of_turn(self, partial_transcript: str, silence_ms: int) -> bool:
        raise NotImplementedError("Phase 3")


class CustomTurnDetector:
    """(c) My own turn-detection model, loaded from VAANI_TURN_MODEL_PATH. TODO(phase 3)."""
    name = "custom"

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or os.getenv("VAANI_TURN_MODEL_PATH")

    def is_end_of_turn(self, partial_transcript: str, silence_ms: int) -> bool:
        raise NotImplementedError("Phase 3")


def get_turn_detector(name: str | None = None) -> TurnDetector:
    name = name or os.getenv("VAANI_TURN_DETECTOR", "vad")
    return {"vad": VADSilenceDetector, "livekit": LiveKitTurnDetector, "custom": CustomTurnDetector}[name]()
