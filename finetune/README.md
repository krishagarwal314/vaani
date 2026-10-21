# Phase 4: speech model fine-tuning (planned)

## STT: Whisper-small + LoRA on Hindi-English code-switched speech
- Candidate data: MUCS 2021 code-switching corpus, AI4Bharat IndicVoices. **Licences still to be verified**
  before any use.
- Plus a small self-recorded loan-domain set: amounts in lakhs/crores, EMI, tenure, Indian names.
- Strict speaker-disjoint train/val/test split; the test set is never used in training or model selection.
- Report WER before/after and number-only WER (`eval/wer.py`), compared against Deepgram on the same set.
- Single GPU (Lightning AI), runs logged, adapter pushed to Hugging Face Hub.

## TTS: Indic Parler-TTS
- Consistent warm Indian-English/Hinglish voice through voice descriptions; light fine-tuning if feasible.
- Compare time-to-first-byte against ElevenLabs; blind MOS (1–5) with 5+ listeners.

`whisper_lora.py` holds the training config. The training loop is not implemented yet.
