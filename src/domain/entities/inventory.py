"""Inventory entity - Aggregate root for inventory management"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..value_objects.stock_quantity import StockQuantity
from ..events.inventory_events import (
    StockAdded,
    StockReserved,
    ReservationCommitted,
    ReservationReleased,
    StockAdjusted,
)
from ..exceptions.inventory_exceptions import (
    InsufficientStockError,
    ReservationNotFoundError,
)


@dataclass
class Reservation:
    """Represents a stock reservation"""
    id: UUID
    quantity: int
    customer_id: UUID
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if reservation has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class Inventory:
    """
    Inventory aggregate root.
    
    Manages stock levels, reservations, and emits domain events.
    Implements optimistic locking via version number.
    """
    product_id: UUID
    store_id: UUID
    available: StockQuantity = field(default_factory=lambda: StockQuantity(0))
    reserved: StockQuantity = field(default_factory=lambda: StockQuantity(0))
    version: int = 0
    reservations: Dict[UUID, Reservation] = field(default_factory=dict)
    pending_events: List = field(default_factory=list)
    
    def add_stock(self, quantity: int, reason: str) -> None:
        """
        Add stock to inventory.
        
        Args:
            quantity: Amount to add
            reason: Reason for addition (e.g., 'restock', 'return')
        
        Raises:
            InvalidQuantityError: If quantity is invalid
        """
        delta = StockQuantity(quantity)
        self.available = self.available.add(delta)
        self.version += 1
        
        event = StockAdded(
            aggregate_id=self._aggregate_id(),
            product_id=self.product_id,
            store_id=self.store_id,
            quantity=quantity,
            reason=reason,
            timestamp=datetime.utcnow(),
            version=self.version,
        )
        self.pending_events.append(event)
    
    def reserve_stock(
        self, 
        quantity: int, 
        customer_id: UUID,
        expires_at: Optional[datetime] = None
    ) -> UUID:
        """
        Reserve stock for a customer.
        
        Args:
            quantity: Amount to reserve
            customer_id: Customer making the reservation
            expires_at: Optional expiration time for the reservation
        
        Returns:
            Reservation ID
        
        Raises:
            InsufficientStockError: If not enough stock available
            InvalidQuantityError: If quantity is invalid
        """
        delta = StockQuantity(quantity)
        
        if self.available.value < quantity:
            raise InsufficientStockError(
                f"Insufficient stock: available={self.available.value}, "
                f"requested={quantity}"
            )
        
        reservation_id = uuid4()
        reservation = Reservation(
            id=reservation_id,
            quantity=quantity,
            customer_id=customer_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        
        self.reservations[reservation_id] = reservation
        self.available = self.available.subtract(delta)
        self.reserved = self.reserved.add(delta)
        self.version += 1
        
        event = StockReserved(
            aggregate_id=self._aggregate_id(),
            product_id=self.product_id,
            store_id=self.store_id,
            reservation_id=reservation_id,
            customer_id=customer_id,
            quantity=quantity,
            timestamp=datetime.utcnow(),
            version=self.version,
        )
        self.pending_events.append(event)
        
        return reservation_id
    
    def commit_reservation(self, reservation_id: UUID, order_id: UUID) -> None:
        """
        Commit a reservation (complete the order).
        
        Args:
            reservation_id: ID of the reservation to commit
            order_id: Associated order ID
        
        Raises:
            ReservationNotFoundError: If reservation doesn't exist
        """
        if reservation_id not in self.reservations:
            raise ReservationNotFoundError(
                f"Reservation {reservation_id} not found"
            )
        
        reservation = self.reservations.pop(reservation_id)
        delta = StockQuantity(reservation.quantity)
        self.reserved = self.reserved.subtract(delta)
        self.version += 1
        
        event = ReservationCommitted(
            aggregate_id=self._aggregate_id(),
            product_id=self.product_id,
            store_id=self.store_id,
            reservation_id=reservation_id,
            order_id=order_id,
            quantity=reservation.quantity,
            timestamp=datetime.utcnow(),
            version=self.version,
        )
        self.pending_events.append(event)
    
    def release_reservation(self, reservation_id: UUID, reason: str) -> None:
        """
        Release a reservation (cancel).
        
        Args:
            reservation_id: ID of the reservation to release
            reason: Reason for release (e.g., 'cancellation', 'timeout')
        
        Raises:
            ReservationNotFoundError: If reservation doesn't exist
        """
        if reservation_id not in self.reservations:
            raise ReservationNotFoundError(
                f"Reservation {reservation_id} not found"
            )
        
        reservation = self.reservations.pop(reservation_id)
        delta = StockQuantity(reservation.quantity)
        self.reserved = self.reserved.subtract(delta)
        self.available = self.available.add(delta)
        self.version += 1
        
        event = ReservationReleased(
            aggregate_id=self._aggregate_id(),
            product_id=self.product_id,
            store_id=self.store_id,
            reservation_id=reservation_id,
            reason=reason,
            quantity=reservation.quantity,
            timestamp=datetime.utcnow(),
            version=self.version,
        )
        self.pending_events.append(event)
    
    def adjust_stock(self, new_quantity: int, reason: str) -> None:
        """
        Adjust stock to a specific quantity (for corrections).
        
        Args:
            new_quantity: Target quantity
            reason: Reason for adjustment
        
        Raises:
            InvalidQuantityError: If quantity is invalid
        """
        new_stock = StockQuantity(new_quantity)
        old_quantity = self.available.value
        self.available = new_stock
        self.version += 1
        
        event = StockAdjusted(
            aggregate_id=self._aggregate_id(),
            product_id=self.product_id,
            store_id=self.store_id,
            old_quantity=old_quantity,
            new_quantity=new_quantity,
            reason=reason,
            timestamp=datetime.utcnow(),
            version=self.version,
        )
        self.pending_events.append(event)
    
    def total_stock(self) -> int:
        """Get total stock (available + reserved)"""
        return self.available.value + self.reserved.value
    
    def clear_events(self) -> List:
        """Clear and return pending events"""
        events = self.pending_events.copy()
        self.pending_events.clear()
        return events
    
    def _aggregate_id(self) -> str:
        """Generate aggregate ID for events"""
        return f"{self.product_id}:{self.store_id}"
