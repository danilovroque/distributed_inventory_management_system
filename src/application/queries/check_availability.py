"""Check Availability query and handler"""
from dataclasses import dataclass
from uuid import UUID

from ...infrastructure.persistence.read_model_repository import ReadModelRepository


@dataclass
class CheckAvailabilityQuery:
    """Query to check if stock is available"""
    product_id: UUID
    store_id: UUID
    required_quantity: int


@dataclass
class AvailabilityResult:
    """Result of availability check"""
    available: bool
    current_stock: int
    required: int


class CheckAvailabilityHandler:
    """Handler for CheckAvailabilityQuery"""
    
    def __init__(self, read_model_repo: ReadModelRepository):
        self.read_model_repo = read_model_repo
    
    async def handle(self, query: CheckAvailabilityQuery) -> AvailabilityResult:
        """Handle check availability query"""
        stock = self.read_model_repo.get_stock(query.product_id, query.store_id)
        
        if not stock:
            return AvailabilityResult(
                available=False,
                current_stock=0,
                required=query.required_quantity
            )
        
        is_available = stock['available'] >= query.required_quantity
        
        return AvailabilityResult(
            available=is_available,
            current_stock=stock['available'],
            required=query.required_quantity
        )
