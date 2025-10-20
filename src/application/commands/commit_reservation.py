"""Commit Reservation command and handler"""
from dataclasses import dataclass
from uuid import UUID

from .add_stock import AddStockHandler


@dataclass
class CommitReservationCommand:
    """Command to commit a reservation"""
    product_id: UUID
    store_id: UUID
    reservation_id: UUID
    order_id: UUID


class CommitReservationHandler(AddStockHandler):
    """Handler for CommitReservationCommand"""
    
    async def handle(self, command: CommitReservationCommand) -> None:
        """Handle commit reservation command"""
        aggregate_id = f"{command.product_id}:{command.store_id}"
        events = await self.event_store.load_events(aggregate_id)
        
        inventory = self._rebuild_from_events(events, command.product_id, command.store_id)
        
        # Commit reservation
        inventory.commit_reservation(command.reservation_id, command.order_id)
        
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
