"""Add Stock command and handler"""
from dataclasses import dataclass
from uuid import UUID

from ...domain.entities.inventory import Inventory
from ...domain.value_objects.stock_quantity import StockQuantity
from ...infrastructure.persistence.event_store import EventStore
from ...infrastructure.persistence.read_model_repository import ReadModelRepository
from ...infrastructure.messaging.event_bus import EventBus


@dataclass
class AddStockCommand:
    """Command to add stock to inventory"""
    product_id: UUID
    store_id: UUID
    quantity: int
    reason: str


class AddStockHandler:
    """Handler for AddStockCommand"""
    
    def __init__(
        self,
        event_store: EventStore,
        read_model_repo: ReadModelRepository,
        event_bus: EventBus
    ):
        self.event_store = event_store
        self.read_model_repo = read_model_repo
        self.event_bus = event_bus
    
    async def handle(self, command: AddStockCommand) -> None:
        """
        Handle add stock command.
        
        Args:
            command: AddStockCommand instance
        """
        # Load aggregate
        aggregate_id = f"{command.product_id}:{command.store_id}"
        events = await self.event_store.load_events(aggregate_id)
        
        # Reconstruct or create inventory
        if events:
            inventory = self._rebuild_from_events(events, command.product_id, command.store_id)
        else:
            inventory = Inventory(
                product_id=command.product_id,
                store_id=command.store_id
            )
        
        # Execute domain logic
        inventory.add_stock(command.quantity, command.reason)
        
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
    
    def _rebuild_from_events(
        self, 
        events: list, 
        product_id: UUID, 
        store_id: UUID
    ) -> Inventory:
        """Rebuild inventory from events (event sourcing)"""
        inventory = Inventory(product_id=product_id, store_id=store_id)
        
        for event in events:
            if event.event_type == "StockAdded":
                inventory.available = inventory.available.add(
                    StockQuantity(event.quantity)
                )
            elif event.event_type == "StockReserved":
                inventory.available = inventory.available.subtract(
                    StockQuantity(event.quantity)
                )
                inventory.reserved = inventory.reserved.add(
                    StockQuantity(event.quantity)
                )
            elif event.event_type == "ReservationCommitted":
                inventory.reserved = inventory.reserved.subtract(
                    StockQuantity(event.quantity)
                )
            elif event.event_type == "ReservationReleased":
                inventory.reserved = inventory.reserved.subtract(
                    StockQuantity(event.quantity)
                )
                inventory.available = inventory.available.add(
                    StockQuantity(event.quantity)
                )
            elif event.event_type == "StockAdjusted":
                inventory.available = StockQuantity(event.new_quantity)
            
            inventory.version = event.version
        
        return inventory
