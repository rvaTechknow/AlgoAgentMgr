"""Data ingestion stubs for market data providers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class IngestionJob:
    provider: str
    symbol: str
    timeframe: str
    start: str
    end: str


class ProviderClient(Protocol):
    def fetch_candles(self, symbol: str, timeframe: str, start: str, end: str) -> list[dict]:
        """Fetch historical candles from provider."""


class DataIngestionService:
    def __init__(self, client: ProviderClient) -> None:
        self.client = client

    def run(self, job: IngestionJob) -> dict:
        return {"status": "stub", "provider": job.provider, "symbol": job.symbol}
