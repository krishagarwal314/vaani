from agent.llm.base import LLM


def get_llm(name: str) -> LLM:
    if name == "mock":
        from agent.llm.mock import MockLLM
        return MockLLM()
    if name == "openai":
        from agent.llm.openai_llm import OpenAILLM
        return OpenAILLM()
    raise ValueError(f"unknown LLM backend: {name}")
