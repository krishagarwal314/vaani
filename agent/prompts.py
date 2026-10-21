"""Load per-stage prompt files and build the system prompt for one LLM step."""
from __future__ import annotations

import hashlib
import json
from functools import cache
from pathlib import Path

from agent.schema import LLMTurnOutput
from agent.stages import Stage

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@cache
def load(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text()


@cache
def prompt_version() -> str:
    """Content hash of every prompt file, so each transcript records exactly which prompts produced it."""
    h = hashlib.sha256()
    for path in sorted(PROMPTS_DIR.glob("*.md")):
        h.update(path.name.encode() + b"\0" + path.read_bytes())
    return "p-" + h.hexdigest()[:12]


def build_system_prompt(stage: Stage, state: dict, tool_schemas: list[dict]) -> str:
    return "\n\n".join([
        load("base"),
        load(stage.value),
        "## Call state\n" + json.dumps(state, ensure_ascii=False, default=str, indent=2),
        "## Tools you may call in this stage\n" + (json.dumps(tool_schemas, indent=2) if tool_schemas else "none"),
        "## Output JSON schema\n" + json.dumps(LLMTurnOutput.model_json_schema()),
    ])
