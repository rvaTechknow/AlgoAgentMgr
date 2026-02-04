"""Shared domain models for API, backtest, and execution services."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Venue(str, Enum):
    HYPERLIQUID = "hyperliquid"
    ROBINHOOD = "robinhood"
    PAPER = "paper"


class Timeframe(str, Enum):
    ONE_MIN = "1m"
    FIVE_MIN = "5m"
    ONE_HOUR = "1h"
    FOUR_HOUR = "4h"
    ONE_DAY = "1d"


class BotStatus(str, Enum):
    DRAFT = "draft"
    BACKTESTED = "backtested"
    PAPER = "paper"
    LIVE = "live"
    PAUSED = "paused"
    STOPPED = "stopped"


class BotSpec(BaseModel):
    bot_id: str
    name: str
    strategy_id: str
    venue: Venue
    status: BotStatus
    created_at: datetime
    updated_at: datetime


class OrderIntent(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str
    limit_price: Optional[float] = None
    time_in_force: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
