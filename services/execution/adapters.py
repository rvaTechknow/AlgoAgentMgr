"""Broker adapter interfaces and stub implementations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from packages.shared.models import OrderIntent, Venue


@dataclass
class OrderResult:
    order_id: str
    status: str
    filled_qty: float
    avg_price: float | None = None


class BrokerAdapter(Protocol):
    venue: Venue

    def submit_order(self, intent: OrderIntent) -> OrderResult:
        """Submit an order to a live or paper venue."""

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""


class PaperAdapter:
    venue = Venue.PAPER

    def submit_order(self, intent: OrderIntent) -> OrderResult:
        return OrderResult(order_id="paper-001", status="filled", filled_qty=intent.quantity, avg_price=intent.limit_price)

    def cancel_order(self, order_id: str) -> bool:
        return True


class RobinhoodStubAdapter:
    venue = Venue.ROBINHOOD

    def submit_order(self, intent: OrderIntent) -> OrderResult:
        return OrderResult(order_id="rh-stub-001", status="accepted", filled_qty=0.0)

    def cancel_order(self, order_id: str) -> bool:
        return True
