"""End-to-end API tests"""
import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def client():
    """Create test client with proper ASGI transport"""
    # Manually trigger the lifespan context
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_add_stock(client):
    """Test adding stock via API"""
    data = {
        "product_id": str(uuid4()),
        "store_id": str(uuid4()),
        "quantity": 100,
        "reason": "restock"
    }
    response = await client.post("/api/v1/inventory/stock", json=data)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_reserve_stock(client):
    """Test reserving stock via API"""
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


@pytest.mark.asyncio
async def test_add_stock_invalid_quantity(client):
    """Test adding stock with invalid quantity returns validation error"""
    data = {
        "product_id": str(uuid4()),
        "store_id": str(uuid4()),
        "quantity": -10,  # Negative quantity should be rejected
        "reason": "restock"
    }
    response = await client.post("/api/v1/inventory/stock", json=data)
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_add_stock_invalid_uuid(client):
    """Test adding stock with invalid UUID returns validation error"""
    data = {
        "product_id": "not-a-valid-uuid",
        "store_id": str(uuid4()),
        "quantity": 100,
        "reason": "restock"
    }
    response = await client.post("/api/v1/inventory/stock", json=data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reserve_insufficient_stock(client):
    """Test reserving more than available stock returns conflict error"""
    product_id = str(uuid4())
    store_id = str(uuid4())
    
    # Add 10 units
    await client.post("/api/v1/inventory/stock", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 10,
        "reason": "restock"
    })
    
    # Try to reserve 20 units (more than available)
    response = await client.post("/api/v1/inventory/reserve", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 20,
        "customer_id": str(uuid4())
    })
    assert response.status_code == 409  # Conflict


@pytest.mark.asyncio
async def test_get_stock_not_found(client):
    """Test getting stock for non-existent product returns 404"""
    product_id = uuid4()
    store_id = uuid4()
    
    response = await client.get(
        f"/api/v1/inventory/products/{product_id}/stores/{store_id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_full_reservation_flow(client):
    """Test complete reservation flow: add, reserve, commit"""
    product_id = str(uuid4())
    store_id = str(uuid4())
    customer_id = str(uuid4())
    order_id = str(uuid4())
    
    # 1. Add stock
    response = await client.post("/api/v1/inventory/stock", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 100,
        "reason": "restock"
    })
    assert response.status_code == 201
    
    # 2. Reserve stock
    response = await client.post("/api/v1/inventory/reserve", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 10,
        "customer_id": customer_id
    })
    assert response.status_code == 201
    reservation_id = response.json()["reservation_id"]
    
    # 3. Commit reservation
    response = await client.post("/api/v1/inventory/commit", json={
        "product_id": product_id,
        "store_id": store_id,
        "reservation_id": reservation_id,
        "order_id": order_id
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_release_reservation_flow(client):
    """Test reservation release flow"""
    product_id = str(uuid4())
    store_id = str(uuid4())
    customer_id = str(uuid4())
    
    # 1. Add stock
    await client.post("/api/v1/inventory/stock", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 100,
        "reason": "restock"
    })
    
    # 2. Reserve stock
    response = await client.post("/api/v1/inventory/reserve", json={
        "product_id": product_id,
        "store_id": store_id,
        "quantity": 10,
        "customer_id": customer_id
    })
    reservation_id = response.json()["reservation_id"]
    
    # 3. Release reservation
    response = await client.post("/api/v1/inventory/release", json={
        "product_id": product_id,
        "store_id": store_id,
        "reservation_id": reservation_id,
        "reason": "customer_cancelled"
    })
    assert response.status_code == 200
