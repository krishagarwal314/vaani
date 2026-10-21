# Results

Benchmarks for the voice pipeline and speech models. Each number comes from a re-runnable script in `eval/`.


| Metric | Value | Source |
|---|---|---|
| Voice-to-voice latency, median / p95 (n calls) | pending | `python eval/latency_report.py transcripts/` |
| Talk-over rate: VAD only / LiveKit detector / custom model | pending | `python eval/talk_over.py transcripts/` |
| Whisper-small WER, held-out test: base → LoRA | pending | `python eval/wer.py` |
| Number/amount WER: base → LoRA | pending | `python eval/wer.py` |
| Deepgram WER, same test set | pending | `python eval/wer.py` |
| TTS time-to-first-byte: Parler-TTS vs ElevenLabs | pending | — |
| TTS MOS (1–5, 5+ listeners) | pending | — |
