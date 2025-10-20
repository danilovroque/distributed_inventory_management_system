"""Inventory Service - Orchestrates commands and queries"""
from uuid import UUID
from typing import Optional, List, Dict

from ..commands.add_stock import AddStockCommand, AddStockHandler
from ..commands.reserve_stock import ReserveStockCommand, ReserveStockHandler
from ..commands.commit_reservation import CommitReservationCommand, CommitReservationHandler
from ..commands.release_reservation import ReleaseReservationCommand, ReleaseReservationHandler
from ..queries.get_stock import GetStockQuery, GetStockHandler
from ..queries.check_availability import CheckAvailabilityQuery, CheckAvailabilityHandler, AvailabilityResult
from ..queries.get_product_inventory import GetProductInventoryQuery, GetProductInventoryHandler


class InventoryService:
    """
    Application service for inventory operations.
    Orchestrates commands and queries.
    """
    
    def __init__(
        self,
        add_stock_handler: AddStockHandler,
        reserve_stock_handler: ReserveStockHandler,
        commit_handler: CommitReservationHandler,
        release_handler: ReleaseReservationHandler,
        get_stock_handler: GetStockHandler,
        check_availability_handler: CheckAvailabilityHandler,
        get_product_inventory_handler: GetProductInventoryHandler
    ):
        self.add_stock_handler = add_stock_handler
        self.reserve_stock_handler = reserve_stock_handler
        self.commit_handler = commit_handler
        self.release_handler = release_handler
        self.get_stock_handler = get_stock_handler
        self.check_availability_handler = check_availability_handler
        self.get_product_inventory_handler = get_product_inventory_handler
    
    # Commands
    async def add_stock(
        self,
        product_id: UUID,
        store_id: UUID,
        quantity: int,
        reason: str
    ) -> None:
        """Add stock"""
        command = AddStockCommand(product_id, store_id, quantity, reason)
        await self.add_stock_handler.handle(command)
    
    async def reserve_stock(
        self,
        product_id: UUID,
        store_id: UUID,
        quantity: int,
        customer_id: UUID,
        ttl_minutes: Optional[int] = 30
    ) -> UUID:
        """Reserve stock"""
        command = ReserveStockCommand(
            product_id, store_id, quantity, customer_id, ttl_minutes
        )
        return await self.reserve_stock_handler.handle(command)
    
    async def commit_reservation(
        self,
        product_id: UUID,
        store_id: UUID,
        reservation_id: UUID,
        order_id: UUID
    ) -> None:
        """Commit reservation"""
        command = CommitReservationCommand(
            product_id, store_id, reservation_id, order_id
        )
        await self.commit_handler.handle(command)
    
    async def release_reservation(
        self,
        product_id: UUID,
        store_id: UUID,
        reservation_id: UUID,
        reason: str
    ) -> None:
        """Release reservation"""
        command = ReleaseReservationCommand(
            product_id, store_id, reservation_id, reason
        )
        await self.release_handler.handle(command)
    
    # Queries
    async def get_stock(
        self,
        product_id: UUID,
        store_id: UUID
    ) -> Optional[Dict]:
        """Get stock"""
        query = GetStockQuery(product_id, store_id)
        return await self.get_stock_handler.handle(query)
    
    async def check_availability(
        self,
        product_id: UUID,
        store_id: UUID,
        required_quantity: int
    ) -> AvailabilityResult:
        """Check availability"""
        query = CheckAvailabilityQuery(product_id, store_id, required_quantity)
        return await self.check_availability_handler.handle(query)
    
    async def get_product_inventory(
        self,
        product_id: UUID
    ) -> List[Dict]:
        """Get product inventory across all stores"""
        query = GetProductInventoryQuery(product_id)
        return await self.get_product_inventory_handler.handle(query)
