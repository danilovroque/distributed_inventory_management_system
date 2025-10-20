"""StockQuantity value object - Immutable quantity representation"""
from dataclasses import dataclass

from ..exceptions.inventory_exceptions import InvalidQuantityError


@dataclass(frozen=True)
class StockQuantity:
    """
    Value object representing a stock quantity.
    
    Ensures quantity is always valid (non-negative).
    Immutable to prevent accidental mutations.
    """
    value: int
    
    def __post_init__(self):
        """Validate quantity on creation"""
        if self.value < 0:
            raise InvalidQuantityError(
                f"Stock quantity cannot be negative: {self.value}"
            )
    
    def add(self, other: "StockQuantity") -> "StockQuantity":
        """
        Add two quantities.
        
        Args:
            other: Quantity to add
        
        Returns:
            New StockQuantity with sum
        """
        return StockQuantity(self.value + other.value)
    
    def subtract(self, other: "StockQuantity") -> "StockQuantity":
        """
        Subtract a quantity.
        
        Args:
            other: Quantity to subtract
        
        Returns:
            New StockQuantity with difference
        
        Raises:
            InvalidQuantityError: If result would be negative
        """
        result = self.value - other.value
        if result < 0:
            raise InvalidQuantityError(
                f"Subtraction would result in negative quantity: "
                f"{self.value} - {other.value} = {result}"
            )
        return StockQuantity(result)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, StockQuantity):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False
    
    def __lt__(self, other) -> bool:
        if isinstance(other, StockQuantity):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented
    
    def __le__(self, other) -> bool:
        if isinstance(other, StockQuantity):
            return self.value <= other.value
        if isinstance(other, int):
            return self.value <= other
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        if isinstance(other, StockQuantity):
            return self.value > other.value
        if isinstance(other, int):
            return self.value > other
        return NotImplemented
    
    def __ge__(self, other) -> bool:
        if isinstance(other, StockQuantity):
            return self.value >= other.value
        if isinstance(other, int):
            return self.value >= other
        return NotImplemented
