"""Unit tests for StockQuantity value object"""
import pytest
from src.domain.value_objects.stock_quantity import StockQuantity
from src.domain.exceptions.inventory_exceptions import InvalidQuantityError


def test_create_valid_quantity():
    """Test creating valid quantity"""
    qty = StockQuantity(10)
    assert qty.value == 10


def test_create_zero_quantity():
    """Test creating zero quantity"""
    qty = StockQuantity(0)
    assert qty.value == 0


def test_create_negative_quantity_raises_error():
    """Test that negative quantity raises error"""
    with pytest.raises(InvalidQuantityError):
        StockQuantity(-1)


def test_add_quantities():
    """Test adding quantities"""
    qty1 = StockQuantity(10)
    qty2 = StockQuantity(5)
    result = qty1.add(qty2)
    assert result.value == 15


def test_subtract_quantities():
    """Test subtracting quantities"""
    qty1 = StockQuantity(10)
    qty2 = StockQuantity(5)
    result = qty1.subtract(qty2)
    assert result.value == 5


def test_subtract_more_than_available_raises_error():
    """Test subtracting more than available raises error"""
    qty1 = StockQuantity(5)
    qty2 = StockQuantity(10)
    with pytest.raises(InvalidQuantityError):
        qty1.subtract(qty2)


def test_equality():
    """Test quantity equality"""
    qty1 = StockQuantity(10)
    qty2 = StockQuantity(10)
    assert qty1 == qty2


def test_comparison_operators():
    """Test comparison operators"""
    qty1 = StockQuantity(5)
    qty2 = StockQuantity(10)
    
    assert qty1 < qty2
    assert qty2 > qty1
    assert qty1 <= qty2
    assert qty2 >= qty1
