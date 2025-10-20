"""Get Stock query and handler"""
from dataclasses import dataclass
from typing import Optional, Dict
from uuid import UUID

from ...infrastructure.persistence.read_model_repository import ReadModelRepository
from ...infrastructure.cache.in_memory_cache import InMemoryCache


@dataclass
class GetStockQuery:
    """Query to get stock for a product at a store"""
    product_id: UUID
    store_id: UUID


class GetStockHandler:
    """Handler for GetStockQuery"""
    
    def __init__(
        self,
        read_model_repo: ReadModelRepository,
        cache: InMemoryCache
    ):
        self.read_model_repo = read_model_repo
        self.cache = cache
    
    async def handle(self, query: GetStockQuery) -> Optional[Dict]:
        """Handle get stock query with caching"""
        cache_key = f"stock:{query.product_id}:{query.store_id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query read model
        stock = self.read_model_repo.get_stock(query.product_id, query.store_id)
        
        # Cache result
        if stock:
            await self.cache.set(cache_key, stock)
        
        return stock
