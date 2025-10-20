"""Inventory API endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from typing import List

from ..schemas.inventory_schemas import (
    AddStockRequest,
    ReserveStockRequest,
    CommitReservationRequest,
    ReleaseReservationRequest,
    CheckAvailabilityRequest,
    StockResponse,
    AvailabilityResponse,
    ProductInventoryResponse,
)
from .....application.services.inventory_service import InventoryService
from .....domain.exceptions.inventory_exceptions import (
    InsufficientStockError,
    ReservationNotFoundError,
    ConcurrencyError,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Dependency injection (will be set by main.py)
_inventory_service: InventoryService = None


def get_inventory_service() -> InventoryService:
    """Dependency to get inventory service"""
    if _inventory_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service not initialized"
        )
    return _inventory_service


def set_inventory_service(service: InventoryService):
    """Set inventory service instance"""
    global _inventory_service
    _inventory_service = service


@router.post("/stock", status_code=status.HTTP_201_CREATED)
async def add_stock(
    request: AddStockRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """Add stock to inventory"""
    try:
        await service.add_stock(
            request.product_id,
            request.store_id,
            request.quantity,
            request.reason
        )
        return {"message": "Stock added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/reserve", status_code=status.HTTP_201_CREATED)
async def reserve_stock(
    request: ReserveStockRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """Reserve stock"""
    try:
        reservation_id = await service.reserve_stock(
            request.product_id,
            request.store_id,
            request.quantity,
            request.customer_id,
            request.ttl_minutes
        )
        return {
            "message": "Stock reserved successfully",
            "reservation_id": str(reservation_id)
        }
    except InsufficientStockError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/commit", status_code=status.HTTP_200_OK)
async def commit_reservation(
    request: CommitReservationRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """Commit a reservation"""
    try:
        await service.commit_reservation(
            request.product_id,
            request.store_id,
            request.reservation_id,
            request.order_id
        )
        return {"message": "Reservation committed successfully"}
    except ReservationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/release", status_code=status.HTTP_200_OK)
async def release_reservation(
    request: ReleaseReservationRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """Release a reservation"""
    try:
        await service.release_reservation(
            request.product_id,
            request.store_id,
            request.reservation_id,
            request.reason
        )
        return {"message": "Reservation released successfully"}
    except ReservationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/products/{product_id}/stores/{store_id}", response_model=StockResponse)
async def get_stock(
    product_id: UUID,
    store_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get stock for a product at a specific store"""
    stock = await service.get_stock(product_id, store_id)
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )
    
    return stock


@router.post("/availability", response_model=AvailabilityResponse)
async def check_availability(
    request: CheckAvailabilityRequest,
    service: InventoryService = Depends(get_inventory_service)
):
    """Check if stock is available"""
    result = await service.check_availability(
        request.product_id,
        request.store_id,
        request.required_quantity
    )
    
    return AvailabilityResponse(
        available=result.available,
        current_stock=result.current_stock,
        required=result.required
    )


@router.get("/products/{product_id}", response_model=List[StockResponse])
async def get_product_inventory(
    product_id: UUID,
    service: InventoryService = Depends(get_inventory_service)
):
    """Get inventory for a product across all stores"""
    inventory = await service.get_product_inventory(product_id)
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return inventory
