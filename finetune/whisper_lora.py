"""Whisper-small + LoRA fine-tuning config."""
from dataclasses import dataclass, field


@dataclass
class LoraTrainConfig:
    base_model: str = "openai/whisper-small"
    language: str = "hi"
    lora_r: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    target_modules: list[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    learning_rate: float = 1e-3
    batch_size: int = 16
    max_steps: int = 4000
    eval_steps: int = 500
    hub_repo: str = ""  # e.g. <user>/whisper-small-hinglish-loan-lora


def main() -> None:
    raise NotImplementedError("load data splits, wrap model with peft.LoraConfig, train, push adapter")


if __name__ == "__main__":
    main()
