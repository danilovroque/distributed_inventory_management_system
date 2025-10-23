"""
Basic usage examples for the Inventory Management System.

This script demonstrates the main API operations.
"""

import asyncio
import httpx
from uuid import uuid4


BASE_URL = "http://localhost:8000/api/v1"


async def main():
    """Run basic usage examples."""
    async with httpx.AsyncClient() as client:
        # Generate IDs
        product_id = str(uuid4())
        store_id = str(uuid4())
        customer_id = str(uuid4())
        order_id = str(uuid4())
        
        print("=" * 60)
        print("Inventory Management System - Basic Usage Examples")
        print("=" * 60)
        
        # 1. Health Check (note: health endpoint is not under /api/v1)
        print("\n1. Health Check")
        response = await client.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 2. Add Stock
        print("\n2. Add Stock (100 units)")
        response = await client.post(
            f"{BASE_URL}/inventory/stock",
            json={
                "product_id": product_id,
                "store_id": store_id,
                "quantity": 100,
                "reason": "initial_stock"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 3. Get Stock
        print("\n3. Get Current Stock")
        response = await client.get(
            f"{BASE_URL}/inventory/products/{product_id}/stores/{store_id}"
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 4. Check Availability
        print("\n4. Check Availability (need 50 units)")
        response = await client.post(
            f"{BASE_URL}/inventory/availability",
            json={
                "product_id": product_id,
                "store_id": store_id,
                "required_quantity": 50
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 5. Reserve Stock
        print("\n5. Reserve Stock (10 units)")
        response = await client.post(
            f"{BASE_URL}/inventory/reserve",
            json={
                "product_id": product_id,
                "store_id": store_id,
                "quantity": 10,
                "customer_id": customer_id,
                "ttl_minutes": 30
            }
        )
        print(f"Status: {response.status_code}")
        reservation_data = response.json()
        print(f"Response: {reservation_data}")
        
        if response.status_code == 201:
            reservation_id = reservation_data["reservation_id"]
            
            # 6. Get Stock After Reservation
            print("\n6. Get Stock After Reservation")
            response = await client.get(
                f"{BASE_URL}/inventory/products/{product_id}/stores/{store_id}"
            )
            print(f"Status: {response.status_code}")
            stock_data = response.json()
            print(f"Response: {stock_data}")
            print(f"Available: {stock_data['available']} (should be 90)")
            
            # 7. Commit Reservation
            print("\n7. Commit Reservation (finalize sale)")
            response = await client.post(
                f"{BASE_URL}/inventory/commit",
                json={
                    "product_id": product_id,
                    "store_id": store_id,
                    "reservation_id": reservation_id,
                    "order_id": order_id
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # 8. Final Stock Check
            print("\n8. Final Stock Check")
            response = await client.get(
                f"{BASE_URL}/inventory/products/{product_id}/stores/{store_id}"
            )
            print(f"Status: {response.status_code}")
            final_stock = response.json()
            print(f"Response: {final_stock}")
            print(f"Final quantity: {final_stock['total']} (should be 90)")
        else:
            print("⚠️  Reservation failed, skipping commit and final check steps")
        
        # 9. Test Insufficient Stock
        print("\n9. Test Insufficient Stock (try to reserve 200 units)")
        response = await client.post(
            f"{BASE_URL}/inventory/reserve",
            json={
                "product_id": product_id,
                "store_id": store_id,
                "quantity": 200,
                "customer_id": customer_id,
                "ttl_minutes": 30
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n" + "=" * 60)
        print("Examples completed!")
        print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the API is running on http://localhost:8000")
    print("Start it with: python main.py\n")
    
    try:
        asyncio.run(main())
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
