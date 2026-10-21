from typing import Protocol

from agent.schema import LLMRequest, LLMTurnOutput


class LLM(Protocol):
    """Any backend (OpenAI, Gemini, Claude, offline mock) that maps one request to structured output."""
    name: str

    def generate(self, req: LLMRequest) -> LLMTurnOutput: ...
