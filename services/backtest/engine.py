"""Backtest engine interfaces and orchestration stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from packages.shared.models import Timeframe


@dataclass
class BacktestRequest:
    strategy_id: str
    symbols: list[str]
    timeframes: list[Timeframe]
    start: str
    end: str
    initial_capital: float


class DataLoader(Protocol):
    def load_candles(self, symbol: str, timeframe: Timeframe, start: str, end: str) -> Iterable[dict]:
        """Load historical candles for a symbol/timeframe window."""


class ExecutionModel(Protocol):
    def apply(self, order: dict, market_snapshot: dict) -> dict:
        """Apply slippage/fees/latency and return fill details."""


class BacktestEngine:
    def __init__(self, data_loader: DataLoader, execution_model: ExecutionModel) -> None:
        self.data_loader = data_loader
        self.execution_model = execution_model

    def run(self, request: BacktestRequest) -> dict:
        """Run a backtest and return artifacts."""
        return {
            "status": "stub",
            "strategy_id": request.strategy_id,
            "symbols": request.symbols,
            "timeframes": [tf.value for tf in request.timeframes],
        }
