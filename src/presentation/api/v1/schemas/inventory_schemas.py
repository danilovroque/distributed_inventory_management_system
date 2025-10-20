"""Pydantic schemas for inventory API"""
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, List


class AddStockRequest(BaseModel):
    """Request to add stock"""
    product_id: UUID
    store_id: UUID
    quantity: int = Field(gt=0, description="Quantity to add")
    reason: str = Field(min_length=1, description="Reason for adding stock")


class ReserveStockRequest(BaseModel):
    """Request to reserve stock"""
    product_id: UUID
    store_id: UUID
    quantity: int = Field(gt=0, description="Quantity to reserve")
    customer_id: UUID
    ttl_minutes: Optional[int] = Field(default=30, gt=0, le=1440)


class CommitReservationRequest(BaseModel):
    """Request to commit reservation"""
    product_id: UUID
    store_id: UUID
    reservation_id: UUID
    order_id: UUID


class ReleaseReservationRequest(BaseModel):
    """Request to release reservation"""
    product_id: UUID
    store_id: UUID
    reservation_id: UUID
    reason: str = Field(min_length=1)


class CheckAvailabilityRequest(BaseModel):
    """Request to check availability"""
    product_id: UUID
    store_id: UUID
    required_quantity: int = Field(gt=0)


class StockResponse(BaseModel):
    """Response with stock information"""
    product_id: str
    store_id: str
    available: int
    reserved: int
    total: int


class AvailabilityResponse(BaseModel):
    """Response for availability check"""
    available: bool
    current_stock: int
    required: int


class ProductInventoryResponse(BaseModel):
    """Response with product inventory across stores"""
    product_id: str
    stores: List[StockResponse]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
