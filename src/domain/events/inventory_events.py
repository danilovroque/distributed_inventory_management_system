"""Inventory domain events"""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from .base import DomainEvent


@dataclass
class StockAdded(DomainEvent):
    """Event emitted when stock is added to inventory"""
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 0
    product_id: UUID = None
    store_id: UUID = None
    quantity: int = 0
    reason: str = ""


@dataclass
class StockReserved(DomainEvent):
    """Event emitted when stock is reserved"""
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 0
    product_id: UUID = None
    store_id: UUID = None
    reservation_id: UUID = None
    customer_id: UUID = None
    quantity: int = 0


@dataclass
class ReservationCommitted(DomainEvent):
    """Event emitted when a reservation is committed (order completed)"""
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 0
    product_id: UUID = None
    store_id: UUID = None
    reservation_id: UUID = None
    order_id: UUID = None
    quantity: int = 0


@dataclass
class ReservationReleased(DomainEvent):
    """Event emitted when a reservation is released (cancelled)"""
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 0
    product_id: UUID = None
    store_id: UUID = None
    reservation_id: UUID = None
    reason: str = ""
    quantity: int = 0


@dataclass
class StockAdjusted(DomainEvent):
    """Event emitted when stock is adjusted (correction)"""
    event_id: UUID = field(default_factory=uuid4)
    aggregate_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    version: int = 0
    product_id: UUID = None
    store_id: UUID = None
    old_quantity: int = 0
    new_quantity: int = 0
    reason: str = ""
