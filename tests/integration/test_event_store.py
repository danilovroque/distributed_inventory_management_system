"""Integration tests for Event Store"""
import pytest
from uuid import uuid4
from src.infrastructure.persistence.event_store import EventStore
from src.domain.events.inventory_events import StockAdded
from src.domain.exceptions.inventory_exceptions import ConcurrencyError


@pytest.mark.asyncio
async def test_append_and_load_events():
    """Test appending and loading events"""
    event_store = EventStore(storage_path="data/test_events")
    aggregate_id = f"{uuid4()}:{uuid4()}"
    
    # Create event
    event = StockAdded(
        aggregate_id=aggregate_id,
        product_id=uuid4(),
        store_id=uuid4(),
        quantity=10,
        reason="test",
        version=1
    )
    
    # Append
    await event_store.append_events(aggregate_id, [event], 0)
    
    # Load
    events = await event_store.load_events(aggregate_id)
    
    assert len(events) == 1
    assert events[0].quantity == 10


@pytest.mark.asyncio
async def test_optimistic_locking():
    """Test optimistic locking detects conflicts"""
    event_store = EventStore(storage_path="data/test_events")
    aggregate_id = f"{uuid4()}:{uuid4()}"
    
    # First event
    event1 = StockAdded(
        aggregate_id=aggregate_id,
        product_id=uuid4(),
        store_id=uuid4(),
        quantity=10,
        reason="test1",
        version=1
    )
    await event_store.append_events(aggregate_id, [event1], 0)
    
    # Try to append with wrong version
    event2 = StockAdded(
        aggregate_id=aggregate_id,
        product_id=uuid4(),
        store_id=uuid4(),
        quantity=5,
        reason="test2",
        version=2
    )
    
    with pytest.raises(ConcurrencyError):
        await event_store.append_events(aggregate_id, [event2], 0)
