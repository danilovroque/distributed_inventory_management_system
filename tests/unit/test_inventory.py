"""Unit tests for Inventory entity"""
import pytest
from uuid import uuid4
from src.domain.entities.inventory import Inventory
from src.domain.value_objects.stock_quantity import StockQuantity
from src.domain.exceptions.inventory_exceptions import (
    InsufficientStockError,
    ReservationNotFoundError,
)


def test_create_inventory():
    """Test creating inventory"""
    product_id = uuid4()
    store_id = uuid4()
    inventory = Inventory(product_id=product_id, store_id=store_id)
    
    assert inventory.product_id == product_id
    assert inventory.store_id == store_id
    assert inventory.available.value == 0
    assert inventory.reserved.value == 0


def test_add_stock():
    """Test adding stock"""
    inventory = Inventory(product_id=uuid4(), store_id=uuid4())
    inventory.add_stock(10, "restock")
    
    assert inventory.available.value == 10
    assert len(inventory.pending_events) == 1


def test_reserve_stock():
    """Test reserving stock"""
    inventory = Inventory(product_id=uuid4(), store_id=uuid4())
    inventory.add_stock(10, "restock")
    inventory.clear_events()
    
    customer_id = uuid4()
    reservation_id = inventory.reserve_stock(5, customer_id)
    
    assert inventory.available.value == 5
    assert inventory.reserved.value == 5
    assert reservation_id in inventory.reservations


def test_reserve_more_than_available_raises_error():
    """Test reserving more than available raises error"""
    inventory = Inventory(product_id=uuid4(), store_id=uuid4())
    inventory.add_stock(5, "restock")
    
    with pytest.raises(InsufficientStockError):
        inventory.reserve_stock(10, uuid4())


def test_commit_reservation():
    """Test committing reservation"""
    inventory = Inventory(product_id=uuid4(), store_id=uuid4())
    inventory.add_stock(10, "restock")
    
    reservation_id = inventory.reserve_stock(5, uuid4())
    inventory.clear_events()
    
    inventory.commit_reservation(reservation_id, uuid4())
    
    assert inventory.reserved.value == 0
    assert reservation_id not in inventory.reservations


def test_release_reservation():
    """Test releasing reservation"""
    inventory = Inventory(product_id=uuid4(), store_id=uuid4())
    inventory.add_stock(10, "restock")
    
    reservation_id = inventory.reserve_stock(5, uuid4())
    inventory.clear_events()
    
    inventory.release_reservation(reservation_id, "cancellation")
    
    assert inventory.available.value == 10
    assert inventory.reserved.value == 0
    assert reservation_id not in inventory.reservations
