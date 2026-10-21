"""Voice-to-voice latency report from voice-mode transcripts.

    python eval/latency_report.py transcripts/ [--detector vad]

Voice-to-voice = tts_first_byte_ms - user_eos_ms, per agent turn. Components:
  endpointing->STT final, STT final->LLM first token, LLM first token->TTS first byte.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.common import load_transcripts, percentile  # noqa: E402

COMPONENTS = {
    "stt": ("user_eos_ms", "stt_final_ms"),
    "llm_ttft": ("stt_final_ms", "llm_first_token_ms"),
    "tts_ttfb": ("llm_first_token_ms", "tts_first_byte_ms"),
    "voice_to_voice": ("user_eos_ms", "tts_first_byte_ms"),
}


def collect(transcripts, detector: str | None = None) -> dict[str, list[int]]:
    samples: dict[str, list[int]] = {k: [] for k in COMPONENTS}
    for t in transcripts:
        for turn in t.turns:
            m = turn.metrics
            if m is None or (detector and m.turn_detector != detector):
                continue
            for name, (a, b) in COMPONENTS.items():
                start, end = getattr(m, a), getattr(m, b)
                if start is not None and end is not None:
                    samples[name].append(end - start)
    return samples


def report(samples: dict[str, list[int]], n_calls: int) -> str:
    lines = [f"calls: {n_calls}", f"{'component':<16}{'n':>6}{'median':>9}{'p95':>8}{'p99':>8}"]
    for name, values in samples.items():
        if values:
            lines.append(f"{name:<16}{len(values):>6}{statistics.median(values):>9.0f}"
                         f"{percentile(values, 95):>8.0f}{percentile(values, 99):>8.0f}")
        else:
            lines.append(f"{name:<16}{0:>6}{'-':>9}{'-':>8}{'-':>8}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", nargs="?", default="transcripts")
    parser.add_argument("--detector", choices=["vad", "livekit", "custom"])
    args = parser.parse_args()
    transcripts = [t for t in load_transcripts(args.directory) if t.mode == "voice"]
    if not transcripts:
        sys.exit(f"no voice-mode transcripts in {args.directory} (Phase 3 harness not run yet)")
    print(report(collect(transcripts, args.detector), len(transcripts)))


if __name__ == "__main__":
    main()
