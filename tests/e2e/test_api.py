"""End-to-end API tests"""
import pytest
from uuid import uuid4
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_stock():
    """Test adding stock via API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        data = {
            "product_id": str(uuid4()),
            "store_id": str(uuid4()),
            "quantity": 100,
            "reason": "restock"
        }
        response = await client.post("/api/v1/inventory/stock", json=data)
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_reserve_stock():
    """Test reserving stock via API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        product_id = str(uuid4())
        store_id = str(uuid4())
        
        # First add stock
        await client.post("/api/v1/inventory/stock", json={
            "product_id": product_id,
            "store_id": store_id,
            "quantity": 100,
            "reason": "restock"
        })
        
        # Then reserve
        response = await client.post("/api/v1/inventory/reserve", json={
            "product_id": product_id,
            "store_id": store_id,
            "quantity": 10,
            "customer_id": str(uuid4())
        })
        assert response.status_code == 201
        assert "reservation_id" in response.json()
