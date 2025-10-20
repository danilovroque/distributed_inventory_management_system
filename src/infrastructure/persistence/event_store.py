"""Event Store implementation using JSON file storage"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import aiofiles

from ...domain.events.base import DomainEvent
from ...domain.events.inventory_events import (
    StockAdded,
    StockReserved,
    ReservationCommitted,
    ReservationReleased,
    StockAdjusted,
)
from ...domain.exceptions.inventory_exceptions import ConcurrencyError


class EventStore:
    """
    Event Store implementation using JSON file storage.
    
    Provides:
    - Append-only event log
    - Optimistic locking via version numbers
    - Event replay capability
    """
    
    def __init__(self, storage_path: str = "data/events"):
        """
        Initialize event store.
        
        Args:
            storage_path: Directory to store event files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._locks = {}
    
    def _get_lock(self, aggregate_id: str) -> asyncio.Lock:
        """Get or create lock for an aggregate"""
        if aggregate_id not in self._locks:
            self._locks[aggregate_id] = asyncio.Lock()
        return self._locks[aggregate_id]
    
    def _event_file_path(self, aggregate_id: str) -> Path:
        """Get file path for aggregate's events"""
        safe_id = aggregate_id.replace(":", "_")
        return self.storage_path / f"{safe_id}.json"
    
    async def append_events(
        self, 
        aggregate_id: str, 
        events: List[DomainEvent],
        expected_version: int
    ) -> None:
        """
        Append events to the event store with optimistic locking.
        
        Args:
            aggregate_id: Aggregate identifier
            events: List of events to append
            expected_version: Expected current version (for concurrency control)
        
        Raises:
            ConcurrencyError: If version conflict is detected
        """
        if not events:
            return
        
        lock = self._get_lock(aggregate_id)
        async with lock:
            # Load current events
            current_events = await self.load_events(aggregate_id)
            current_version = len(current_events)
            
            # Check optimistic lock
            if current_version != expected_version:
                raise ConcurrencyError(
                    f"Version conflict: expected {expected_version}, "
                    f"found {current_version}"
                )
            
            # Serialize events
            event_dicts = [event.to_dict() for event in events]
            
            # Append to file
            file_path = self._event_file_path(aggregate_id)
            
            if file_path.exists():
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                    stored_events = json.loads(content) if content else []
            else:
                stored_events = []
            
            stored_events.extend(event_dicts)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(stored_events, indent=2))
    
    async def load_events(
        self, 
        aggregate_id: str,
        from_version: Optional[int] = None
    ) -> List[DomainEvent]:
        """
        Load events for an aggregate.
        
        Args:
            aggregate_id: Aggregate identifier
            from_version: Optional starting version (exclusive)
        
        Returns:
            List of domain events
        """
        file_path = self._event_file_path(aggregate_id)
        
        if not file_path.exists():
            return []
        
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            event_dicts = json.loads(content) if content else []
        
        events = []
        for event_dict in event_dicts:
            event = self._deserialize_event(event_dict)
            if from_version is None or event.version > from_version:
                events.append(event)
        
        return events
    
    def _deserialize_event(self, event_dict: dict) -> DomainEvent:
        """Deserialize event from dictionary"""
        event_type = event_dict['event_type']
        
        # Convert string UUIDs back to UUID objects
        for key, value in event_dict.items():
            if key.endswith('_id') and isinstance(value, str):
                try:
                    event_dict[key] = UUID(value)
                except (ValueError, AttributeError):
                    pass
            elif key == 'timestamp' and isinstance(value, str):
                event_dict[key] = datetime.fromisoformat(value)
        
        # Map event type to class
        event_classes = {
            'StockAdded': StockAdded,
            'StockReserved': StockReserved,
            'ReservationCommitted': ReservationCommitted,
            'ReservationReleased': ReservationReleased,
            'StockAdjusted': StockAdjusted,
        }
        
        event_class = event_classes.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        # Remove event_type from dict before creating instance
        event_dict_copy = event_dict.copy()
        event_dict_copy.pop('event_type', None)
        
        return event_class(**event_dict_copy)
    
    async def get_current_version(self, aggregate_id: str) -> int:
        """Get current version of an aggregate"""
        events = await self.load_events(aggregate_id)
        return len(events)
