"""Reserve Stock command and handler"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from .add_stock import AddStockHandler


@dataclass
class ReserveStockCommand:
    """Command to reserve stock"""
    product_id: UUID
    store_id: UUID
    quantity: int
    customer_id: UUID
    ttl_minutes: Optional[int] = 30


class ReserveStockHandler(AddStockHandler):
    """Handler for ReserveStockCommand"""
    
    async def handle(self, command: ReserveStockCommand) -> UUID:
        """Handle reserve stock command"""
        aggregate_id = f"{command.product_id}:{command.store_id}"
        events = await self.event_store.load_events(aggregate_id)
        
        if events:
            inventory = self._rebuild_from_events(events, command.product_id, command.store_id)
        else:
            from ...domain.entities.inventory import Inventory
            inventory = Inventory(product_id=command.product_id, store_id=command.store_id)
        
        # Calculate expiration
        expires_at = None
        if command.ttl_minutes:
            expires_at = datetime.utcnow() + timedelta(minutes=command.ttl_minutes)
        
        # Reserve stock
        reservation_id = inventory.reserve_stock(
            command.quantity,
            command.customer_id,
            expires_at
        )
        
        # Save events
        new_events = inventory.clear_events()
        await self.event_store.append_events(
            aggregate_id,
            new_events,
            inventory.version - len(new_events)
        )
        
        # Update read model
        self.read_model_repo.update_stock(
            command.product_id,
            command.store_id,
            inventory.available.value,
            inventory.reserved.value
        )
        
        # Publish events
        for event in new_events:
            await self.event_bus.publish(event)
        
        return reservation_id
