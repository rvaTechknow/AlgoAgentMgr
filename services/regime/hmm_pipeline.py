"""Hidden Markov Model pipeline stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class HMMConfig:
    states: int
    features: list[str]
    lookback: str
    train_window: str


class RegimeModelRegistry:
    def register(self, metadata: dict[str, Any]) -> str:
        """Register model metadata and return version id."""
        return "regime-model-v0"


class HMMPipeline:
    def __init__(self, registry: RegimeModelRegistry) -> None:
        self.registry = registry

    def train(self, config: HMMConfig) -> dict[str, Any]:
        model_version = self.registry.register({"config": config})
        return {"status": "stub", "model_version": model_version}
