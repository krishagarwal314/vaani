"""LiveKit Agents worker.

Design:
- One CallSession per room; STT finals -> session.handle_user(), VAD silence -> session.handle_silence().
- Stream LLM tokens through SentenceChunker so TTS speaks sentence by sentence.
- On user speech start while TTS is playing: stop playout within one frame, then
  session.handle_barge_in(chars_played) so unspoken text is dropped from history and transcript.
- FillerPolicy covers slow LLM time-to-first-token.
- Record TurnMetrics (user_eos, stt_final, llm_first_token, tts_first_byte) on each agent turn.
- STT: fine-tuned Whisper-small, Deepgram fallback. TTS: Indic Parler-TTS, ElevenLabs fallback.
"""


def main() -> None:
    raise NotImplementedError("LiveKit voice worker")


if __name__ == "__main__":
    main()
