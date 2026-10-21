# Results

Nothing has been measured yet. Each number below will come from a re-runnable script in `eval/`
once the phase that produces it is built.

| Metric | Value | Source |
|---|---|---|
| Voice-to-voice latency, median / p95 (n calls) | TBD (Phase 3) | `python eval/latency_report.py transcripts/` |
| Talk-over rate: VAD only / LiveKit detector / custom model | TBD (Phase 3) | `python eval/talk_over.py transcripts/` |
| Whisper-small WER, held-out test: base → LoRA | TBD (Phase 4) | `python eval/wer.py` |
| Number/amount WER: base → LoRA | TBD (Phase 4) | `python eval/wer.py` |
| Deepgram WER, same test set | TBD (Phase 4) | `python eval/wer.py` |
| TTS time-to-first-byte: Parler-TTS vs ElevenLabs | TBD (Phase 4) | — |
| TTS MOS (1–5, 5+ listeners) | TBD (Phase 4) | — |
