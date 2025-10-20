"""Domain exceptions for inventory management"""


class InventoryDomainError(Exception):
    """Base exception for all inventory domain errors"""
    pass


class InsufficientStockError(InventoryDomainError):
    """Raised when trying to reserve more stock than available"""
    pass


class InvalidQuantityError(InventoryDomainError):
    """Raised when a quantity is invalid (e.g., negative)"""
    pass


class ReservationNotFoundError(InventoryDomainError):
    """Raised when a reservation cannot be found"""
    pass


class ConcurrencyError(InventoryDomainError):
    """Raised when optimistic locking detects a conflict"""
    pass
