"""
Quick start script to initialize the system with sample data.
This script creates sample products and adds initial inventory to multiple stores.

Usage:
    python scripts/init_sample_data.py
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4, UUID
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.application.commands.add_stock import AddStockCommand, AddStockHandler
from src.infrastructure.cache.in_memory_cache import InMemoryCache
from src.infrastructure.messaging.event_bus import EventBus
from src.infrastructure.persistence.event_store import EventStore
from src.infrastructure.persistence.read_model_repository import ReadModelRepository


async def cleanup_data():
    """Clean up existing data files."""
    import shutil
    
    paths = [
        "./data/events",
        "./data/read_models"
    ]
    
    for path in paths:
        path_obj = Path(path)
        if path_obj.exists():
            shutil.rmtree(path_obj)
            print(f"  X Removed {path}")
    
    print()


async def initialize_sample_data():
    """Initialize system with sample products and inventory."""
    
    print("\n" + "=" * 60)
    print("INITIALIZING SAMPLE DATA")
    print("=" * 60 + "\n")
    
    # Confirm before cleanup
    response = input("This will delete existing data. Continue? (y/N): ")
    if response.lower() != 'y':
        print("\n❌ Cancelled.\n")
        return
    
    print("\n🗑️  Cleaning up existing data...")
    await cleanup_data()
    
    # Initialize infrastructure
    print("🔧 Initializing infrastructure...")
    event_store = EventStore("./data/events")
    event_bus = EventBus()
    read_model_repo = ReadModelRepository("./data/read_models")
    cache = InMemoryCache()
    
    # Note: AddStockHandler already updates the read model when processing commands
    # No need to subscribe additional handlers here
    print("  ✓ Infrastructure initialized\n")
    
    # Create handler (ordem correta: event_store, read_model_repo, event_bus)
    add_stock_handler = AddStockHandler(event_store, read_model_repo, event_bus)
    
    # Define products
    products = [
        {
            "id": uuid4(),
            "name": "Gaming Laptop Pro",
            "sku": "LAPTOP-001",
            "price": 1299.99,
            "category": "Electronics"
        },
        {
            "id": uuid4(),
            "name": "Smartphone Pro Max",
            "sku": "PHONE-001",
            "price": 999.99,
            "category": "Electronics"
        },
        {
            "id": uuid4(),
            "name": "Tablet Ultra 12\"",
            "sku": "TABLET-001",
            "price": 599.99,
            "category": "Electronics"
        },
        {
            "id": uuid4(),
            "name": "Smart Watch Sport",
            "sku": "WATCH-001",
            "price": 299.99,
            "category": "Wearables"
        },
        {
            "id": uuid4(),
            "name": "Wireless Headphones Pro",
            "sku": "AUDIO-001",
            "price": 199.99,
            "category": "Audio"
        }
    ]
    
    # Define stores
    stores = [
        {"id": uuid4(), "name": "Downtown Store", "code": "DT-001"},
        {"id": uuid4(), "name": "Mall Store", "code": "ML-001"},
        {"id": uuid4(), "name": "Online Warehouse", "code": "WH-001"}
    ]
    
    print("📦 Products defined:")
    for product in products:
        print(f"  • {product['name']} ({product['sku']})")
    
    print(f"\n🏪 Stores defined:")
    for store in stores:
        print(f"  • {store['name']} ({store['code']})")
    
    print()
    
    # Add inventory for each product in each store
    print("🏪 Adding inventory to stores...")
    
    inventory_data: Dict[str, list] = {}
    total_items = 0
    
    for product in products:
        product_inventory = []
        
        for store in stores:
            # Different quantities per store
            quantity = {
                "DT-001": 50,
                "ML-001": 100,
                "WH-001": 200
            }.get(store["code"], 100)
            
            # Create command
            command = AddStockCommand(
                product_id=product["id"],
                store_id=store["id"],
                quantity=quantity,
                reason="initial_stock"
            )
            
            # Execute command
            result = await add_stock_handler.handle(command)
            
            product_inventory.append({
                "store": store["name"],
                "quantity": quantity
            })
            total_items += quantity
            
            print(f"  ✓ {product['name']} @ {store['name']}: {quantity} units")
        
        inventory_data[product["name"]] = product_inventory
    
    print()
    print("=" * 60)
    print("✅ INITIALIZATION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Products created: {len(products)}")
    print(f"  • Stores: {len(stores)}")
    print(f"  • Total inventory items: {total_items}")
    print(f"  • Event handlers: {event_bus.get_handler_count()}")
    
    # Save IDs to file for reference
    print(f"\n💾 Saving reference data...")
    with open("sample_data_ids.txt", "w") as f:
        f.write("SAMPLE DATA IDs\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("PRODUCTS:\n")
        for product in products:
            f.write(f"  {product['sku']}: {product['id']}\n")
        
        f.write("\nSTORES:\n")
        for store in stores:
            f.write(f"  {store['code']}: {store['id']}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("API EXAMPLES:\n")
        f.write("=" * 60 + "\n\n")
        
        first_product = products[0]
        first_store = stores[0]
        
        f.write("# Check stock:\n")
        f.write(f"GET /api/v1/inventory/products/{first_product['id']}/stores/{first_store['id']}\n\n")
        
        f.write("# Reserve stock:\n")
        f.write(f"""POST /api/v1/inventory/reserve
{{
  "product_id": "{first_product['id']}",
  "store_id": "{first_store['id']}",
  "quantity": 2
}}
\n""")
    
    print(f"  ✓ Saved to: sample_data_ids.txt\n")
    
    print("🚀 Next steps:")
    print("  1. Start the API: python main.py")
    print("  2. Open Swagger UI: http://localhost:8000/swagger")
    print("  3. Use the IDs in sample_data_ids.txt to test\n")


if __name__ == "__main__":
    asyncio.run(initialize_sample_data())