"""Get Product Inventory query and handler"""
from dataclasses import dataclass
from typing import List, Dict
from uuid import UUID

from ...infrastructure.persistence.read_model_repository import ReadModelRepository
from ...infrastructure.cache.in_memory_cache import InMemoryCache


@dataclass
class GetProductInventoryQuery:
    """Query to get inventory for a product across all stores"""
    product_id: UUID


class GetProductInventoryHandler:
    """Handler for GetProductInventoryQuery"""
    
    def __init__(
        self,
        read_model_repo: ReadModelRepository,
        cache: InMemoryCache
    ):
        self.read_model_repo = read_model_repo
        self.cache = cache
    
    async def handle(self, query: GetProductInventoryQuery) -> List[Dict]:
        """Handle get product inventory query"""
        cache_key = f"product_inventory:{query.product_id}"
        
        # Try cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Query read model
        inventory = self.read_model_repo.get_product_inventory(query.product_id)
        
        # Cache result
        if inventory:
            await self.cache.set(cache_key, inventory)
        
        return inventory
