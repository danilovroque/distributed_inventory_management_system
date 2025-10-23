"""
Main FastAPI application entry point
"""
import structlog
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from src.infrastructure.persistence.event_store import EventStore
from src.infrastructure.persistence.read_model_repository import ReadModelRepository
from src.infrastructure.cache.in_memory_cache import InMemoryCache
from src.infrastructure.messaging.event_bus import EventBus
from src.infrastructure.resilience.circuit_breaker import CircuitBreaker

from src.application.commands.add_stock import AddStockHandler
from src.application.commands.reserve_stock import ReserveStockHandler
from src.application.commands.commit_reservation import CommitReservationHandler
from src.application.commands.release_reservation import ReleaseReservationHandler
from src.application.queries.get_stock import GetStockHandler
from src.application.queries.check_availability import CheckAvailabilityHandler
from src.application.queries.get_product_inventory import GetProductInventoryHandler
from src.application.services.inventory_service import InventoryService

from src.presentation.api.v1.endpoints import inventory, health
from src.presentation.middleware.logging_middleware import LoggingMiddleware
from src.domain.exceptions.inventory_exceptions import (
    InsufficientStockError,
    ReservationNotFoundError,
    ConcurrencyError,
    InvalidQuantityError,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("application_starting")
    
    # Initialize infrastructure
    event_store = EventStore()
    read_model_repo = ReadModelRepository()
    cache = InMemoryCache(default_ttl=30)
    event_bus = EventBus()
    
    # Setup event handlers to invalidate cache
    async def invalidate_cache_on_stock_added(event):
        """Invalidate cache when stock is added"""
        logger.info("event_received", event_type="StockAdded", 
                   product_id=str(event.product_id), store_id=str(event.store_id))
        # Invalidate cache
        cache_key = f"stock:{event.product_id}:{event.store_id}"
        await cache.delete(cache_key)
        logger.info("cache_invalidated", event_type="StockAdded")
    
    async def invalidate_cache_on_stock_reserved(event):
        """Invalidate cache when stock is reserved"""
        logger.info("event_received", event_type="StockReserved",
                   product_id=str(event.product_id), store_id=str(event.store_id))
        # Invalidate cache
        cache_key = f"stock:{event.product_id}:{event.store_id}"
        await cache.delete(cache_key)
        logger.info("cache_invalidated", event_type="StockReserved")
    
    async def invalidate_cache_on_reservation_committed(event):
        """Invalidate cache when reservation is committed"""
        logger.info("event_received", event_type="ReservationCommitted",
                   product_id=str(event.product_id), store_id=str(event.store_id))
        # Invalidate cache
        cache_key = f"stock:{event.product_id}:{event.store_id}"
        await cache.delete(cache_key)
        logger.info("cache_invalidated", event_type="ReservationCommitted")
    
    async def invalidate_cache_on_reservation_released(event):
        """Invalidate cache when reservation is released"""
        logger.info("event_received", event_type="ReservationReleased",
                   product_id=str(event.product_id), store_id=str(event.store_id))
        # Invalidate cache
        cache_key = f"stock:{event.product_id}:{event.store_id}"
        await cache.delete(cache_key)
        logger.info("cache_invalidated", event_type="ReservationReleased")
    
    # Subscribe to events
    event_bus.subscribe("StockAdded", invalidate_cache_on_stock_added)
    event_bus.subscribe("StockReserved", invalidate_cache_on_stock_reserved)
    event_bus.subscribe("ReservationCommitted", invalidate_cache_on_reservation_committed)
    event_bus.subscribe("ReservationReleased", invalidate_cache_on_reservation_released)
    
    logger.info("event_handlers_registered", 
               handlers=["StockAdded", "StockReserved", "ReservationCommitted", "ReservationReleased"])
    
    # Initialize command handlers
    add_stock_handler = AddStockHandler(event_store, read_model_repo, event_bus)
    reserve_stock_handler = ReserveStockHandler(event_store, read_model_repo, event_bus)
    commit_handler = CommitReservationHandler(event_store, read_model_repo, event_bus)
    release_handler = ReleaseReservationHandler(event_store, read_model_repo, event_bus)
    
    # Initialize query handlers
    get_stock_handler = GetStockHandler(read_model_repo, cache)
    check_availability_handler = CheckAvailabilityHandler(read_model_repo)
    get_product_inventory_handler = GetProductInventoryHandler(read_model_repo, cache)
    
    # Initialize service
    inventory_service = InventoryService(
        add_stock_handler,
        reserve_stock_handler,
        commit_handler,
        release_handler,
        get_stock_handler,
        check_availability_handler,
        get_product_inventory_handler
    )
    
    # Set service in endpoint module
    inventory.set_inventory_service(inventory_service)
    
    logger.info("application_started")
    yield
    logger.info("application_shutdown")


# Create FastAPI app
app = FastAPI(
    title="Distributed Inventory Management System",
    version="1.0.0",
    description="Event Sourcing and CQRS-based inventory system",
    lifespan=lifespan,
    docs_url="/swagger",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    """Handle insufficient stock errors"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "insufficient_stock", "detail": str(exc)}
    )


@app.exception_handler(ReservationNotFoundError)
async def reservation_not_found_handler(request: Request, exc: ReservationNotFoundError):
    """Handle reservation not found errors"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "reservation_not_found", "detail": str(exc)}
    )


@app.exception_handler(ConcurrencyError)
async def concurrency_error_handler(request: Request, exc: ConcurrencyError):
    """Handle concurrency errors"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "concurrency_conflict", "detail": str(exc)}
    )


@app.exception_handler(InvalidQuantityError)
async def invalid_quantity_handler(request: Request, exc: InvalidQuantityError):
    """Handle invalid quantity errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "invalid_quantity", "detail": str(exc)}
    )


# Include routers
app.include_router(health.router)
app.include_router(inventory.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Distributed Inventory Management System",
        "version": "1.0.0",
        "docs": "/swagger"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("starting_server", host="0.0.0.0", port=8000)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
