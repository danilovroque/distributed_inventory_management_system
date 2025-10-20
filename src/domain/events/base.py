"""Base domain event"""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """
    Base class for all domain events.
    
    Events represent facts that have happened in the domain.
    They are immutable and include:
    - event_id: Unique identifier for this event instance
    - aggregate_id: ID of the aggregate that generated the event
    - timestamp: When the event occurred
    - version: Version of the aggregate after this event
    """
    event_id: UUID
    aggregate_id: str
    timestamp: datetime
    version: int
    
    def __post_init__(self):
        """Generate event_id if not provided"""
        if not hasattr(self, 'event_id') or self.event_id is None:
            object.__setattr__(self, 'event_id', uuid4())
    
    @property
    def event_type(self) -> str:
        """Get the event type name"""
        return self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        result = {
            'event_type': self.event_type,
            'event_id': str(self.event_id),
            'aggregate_id': self.aggregate_id,
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
        }
        
        # Add all other fields
        for field_name, field_value in self.__dict__.items():
            if field_name not in result:
                if isinstance(field_value, UUID):
                    result[field_name] = str(field_value)
                elif isinstance(field_value, datetime):
                    result[field_name] = field_value.isoformat()
                else:
                    result[field_name] = field_value
        
        return result
