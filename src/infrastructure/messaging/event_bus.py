"""Event Bus for pub/sub messaging"""
import asyncio
from typing import Callable, Dict, List, Type, Union
import logging

from ...domain.events.base import DomainEvent


logger = logging.getLogger(__name__)


class EventBus:
    """
    Simple in-memory event bus for pub/sub messaging.
    
    Allows decoupling of event producers and consumers.
    Handlers are called asynchronously.
    """
    
    def __init__(self):
        """Initialize event bus"""
        # Aceita tanto Type quanto string como chave
        self._handlers: Dict[Union[Type[DomainEvent], str], List[Callable]] = {}
        self._lock = asyncio.Lock()
    
    def subscribe(
        self, 
        event_type: Union[Type[DomainEvent], str], 
        handler: Callable
    ):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event or event name string to subscribe to
            handler: Async function to handle event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        
        self._handlers[event_type].append(handler)
        
        # Obter nome do evento (Type ou string)
        event_name = event_type.__name__ if hasattr(event_type, '__name__') else str(event_type)
        handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
        
        logger.debug(
            f"Subscribed {handler_name} to {event_name}"
        )
    
    async def publish(self, event: DomainEvent):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Domain event to publish
        """
        event_type = type(event)
        event_name = event_type.__name__
        
        # Buscar handlers por Type e por string
        handlers = []
        handlers.extend(self._handlers.get(event_type, []))
        handlers.extend(self._handlers.get(event_name, []))
        
        if not handlers:
            logger.debug(f"No handlers for event {event_name}")
            return
        
        logger.debug(
            f"Publishing {event_name} to {len(handlers)} handlers"
        )
        
        # Call all handlers concurrently
        tasks = []
        for handler in handlers:
            task = self._call_handler(handler, event)
            tasks.append(task)
        
        # Wait for all handlers to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any errors
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                handler_name = handlers[idx].__name__ if hasattr(handlers[idx], '__name__') else str(handlers[idx])
                logger.error(
                    f"Error in handler {handler_name} for {event_name}: {result}",
                    exc_info=result
                )
    
    async def _call_handler(self, handler: Callable, event: DomainEvent):
        """Call event handler safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
            logger.error(f"Handler {handler_name} failed: {e}")
            raise
    
    def unsubscribe(
        self, 
        event_type: Union[Type[DomainEvent], str], 
        handler: Callable
    ):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event or event name to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._handlers:
            handlers = self._handlers[event_type]
            if handler in handlers:
                handlers.remove(handler)
                
                event_name = event_type.__name__ if hasattr(event_type, '__name__') else str(event_type)
                handler_name = handler.__name__ if hasattr(handler, '__name__') else str(handler)
                
                logger.debug(
                    f"Unsubscribed {handler_name} from {event_name}"
                )
    
    def clear(self):
        """Clear all subscriptions"""
        self._handlers.clear()
        logger.debug("Cleared all event bus subscriptions")
    
    def get_handler_count(self, event_type: Union[Type[DomainEvent], str] = None) -> int:
        """
        Get number of handlers registered.
        
        Args:
            event_type: Optional event type to count handlers for
            
        Returns:
            Number of handlers
        """
        if event_type:
            return len(self._handlers.get(event_type, []))
        return sum(len(handlers) for handlers in self._handlers.values())