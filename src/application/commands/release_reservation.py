"""Release Reservation command and handler"""
from dataclasses import dataclass
from uuid import UUID

from .add_stock import AddStockHandler


@dataclass
class ReleaseReservationCommand:
    """Command to release a reservation"""
    product_id: UUID
    store_id: UUID
    reservation_id: UUID
    reason: str


class ReleaseReservationHandler(AddStockHandler):
    """Handler for ReleaseReservationCommand"""
    
    async def handle(self, command: ReleaseReservationCommand) -> None:
        """Handle release reservation command"""
        aggregate_id = f"{command.product_id}:{command.store_id}"
        events = await self.event_store.load_events(aggregate_id)
        
        inventory = self._rebuild_from_events(events, command.product_id, command.store_id)
        
        # Release reservation
        inventory.release_reservation(command.reservation_id, command.reason)
        
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
