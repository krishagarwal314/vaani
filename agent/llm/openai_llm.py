"""OpenAI backend (GPT-4o-mini by default) using JSON mode + Pydantic validation."""
from __future__ import annotations

import json
import os

from agent.schema import LLMRequest, LLMTurnOutput

_EVENT_NOTES = {
    "enter": "You have just entered this stage. Say the stage's opening line.",
    "resume": "The caller confirmed the amount you read back. Continue the stage.",
}


class OpenAILLM:
    def __init__(self, model: str | None = None, client=None, max_retries: int = 1):
        if client is None:
            from openai import OpenAI
            client = OpenAI()
        self.client = client
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.name = f"openai:{self.model}"
        self.max_retries = max_retries

    def generate(self, req: LLMRequest) -> LLMTurnOutput:
        messages = [{"role": "system", "content": req.system_prompt}, *req.history]
        if req.event in _EVENT_NOTES:
            messages.append({"role": "system", "content": _EVENT_NOTES[req.event]})
        if req.tool_results:
            results = [r.model_dump(include={"name", "arguments", "result", "error"}) for r in req.tool_results]
            messages.append({"role": "system", "content": "Tool results:\n" + json.dumps(results, default=str)})

        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            resp = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.3,
                response_format={"type": "json_object"},
            )
            try:
                return LLMTurnOutput.model_validate_json(resp.choices[0].message.content)
            except ValueError as e:  # pydantic ValidationError subclasses ValueError
                last_error = e
        raise RuntimeError(f"LLM returned invalid output: {last_error}")
