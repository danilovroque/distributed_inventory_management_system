"""
Quick start script to initialize the system with sample data.
This script creates sample MercadoLibre Brasil products and adds initial inventory 
to multiple fulfillment centers and distribution points.

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
    """Initialize system with sample MercadoLibre Brasil products and inventory."""
    
    print("\n" + "=" * 70)
    print("INICIALIZANDO DADOS DO MERCADO LIVRE BRASIL")
    print("=" * 70 + "\n")
    
    # Confirm before cleanup
    response = input("Isso irá deletar os dados existentes. Continuar? (s/N): ")
    if response.lower() != 's':
        print("\n❌ Cancelado.\n")
        return
    
    print("\n🗑️  Limpando dados existentes...")
    await cleanup_data()
    
    # Initialize infrastructure
    print("🔧 Inicializando infraestrutura...")
    event_store = EventStore("./data/events")
    event_bus = EventBus()
    read_model_repo = ReadModelRepository("./data/read_models")
    cache = InMemoryCache()
    
    # Note: AddStockHandler already updates the read model when processing commands
    # No need to subscribe additional handlers here
    print("  ✓ Infraestrutura inicializada\n")
    
    # Create handler (ordem correta: event_store, read_model_repo, event_bus)
    add_stock_handler = AddStockHandler(event_store, read_model_repo, event_bus)
    
    # Define products (produtos reais do MercadoLibre Brasil)
    products = [
        {
            "id": uuid4(),
            "name": "Samsung Galaxy S24 Ultra 256GB Preto",
            "sku": "MLB-S24U-256-PT",
            "price": 6999.99,
            "category": "Celulares e Smartphones"
        },
        {
            "id": uuid4(),
            "name": "iPhone 15 Pro Max 128GB Titânio Natural",
            "sku": "MLB-IP15PM-128-TN",
            "price": 8999.99,
            "category": "Celulares e Smartphones"
        },
        {
            "id": uuid4(),
            "name": "Notebook Dell Inspiron 15 3000 i5 8GB 256GB SSD",
            "sku": "MLB-DELL-I15-I5-8G",
            "price": 2799.99,
            "category": "Notebooks"
        },
        {
            "id": uuid4(),
            "name": "PlayStation 5 Standard Edition",
            "sku": "MLB-PS5-STD-BR",
            "price": 3899.99,
            "category": "Games e Consoles"
        },
        {
            "id": uuid4(),
            "name": "Apple Watch Series 9 GPS 41mm Meia-noite",
            "sku": "MLB-AW9-GPS-41-MN",
            "price": 2499.99,
            "category": "Smartwatches"
        },
        {
            "id": uuid4(),
            "name": "AirPods Pro 2ª Geração USB-C",
            "sku": "MLB-APP2-USBC-BR",
            "price": 1699.99,
            "category": "Fones de Ouvido"
        },
        {
            "id": uuid4(),
            "name": "Tênis Nike Air Force 1 '07 Branco",
            "sku": "MLB-AF1-07-WHT-BR",
            "price": 649.99,
            "category": "Tênis"
        },
        {
            "id": uuid4(),
            "name": "Smart TV LG 55'' 4K UHD ThinQ AI",
            "sku": "MLB-LG55-4K-THINQ",
            "price": 2199.99,
            "category": "TVs"
        },
        {
            "id": uuid4(),
            "name": "Geladeira Brastemp Frost Free Duplex 462L",
            "sku": "MLB-BRAST-FF-462L",
            "price": 2899.99,
            "category": "Eletrodomésticos"
        },
        {
            "id": uuid4(),
            "name": "Kit Perfume Natura Homem Essence 100ml",
            "sku": "MLB-NAT-HOM-ESS-100",
            "price": 159.99,
            "category": "Perfumaria"
        }
    ]
    
    # Define stores (centros de distribuição e pontos do MercadoLibre Brasil)
    stores = [
        {"id": uuid4(), "name": "Centro de Distribuição São Paulo", "code": "MELI-CD-SP"},
        {"id": uuid4(), "name": "Centro de Distribuição Rio de Janeiro", "code": "MELI-CD-RJ"},
        {"id": uuid4(), "name": "Centro de Distribuição Belo Horizonte", "code": "MELI-CD-BH"},
        {"id": uuid4(), "name": "Fulfillment Center Campinas", "code": "MELI-FC-CP"},
        {"id": uuid4(), "name": "Hub Zona Sul SP", "code": "MELI-HUB-ZS-SP"},
        {"id": uuid4(), "name": "MercadoEnvios Ponto Faria Lima", "code": "MELI-ME-FL"},
        {"id": uuid4(), "name": "Cross Docking Guarulhos", "code": "MELI-XD-GRU"},
        {"id": uuid4(), "name": "Armazém Seller Flex ABC", "code": "MELI-SF-ABC"},
        {"id": uuid4(), "name": "Ponto de Retirada Shopping Iguatemi", "code": "MELI-PR-IGU"},
        {"id": uuid4(), "name": "Centro Logístico Brasília", "code": "MELI-CL-BSB"}
    ]
    
    print("📦 Produtos definidos:")
    for product in products:
        print(f"  • {product['name']} ({product['sku']})")
    
    print(f"\n🏪 Centros de distribuição definidos:")
    for store in stores:
        print(f"  • {store['name']} ({store['code']})")
    
    print()
    
    # Add inventory for each product in each store
    print("🏪 Adicionando inventário aos centros de distribuição...")
    
    inventory_data: Dict[str, list] = {}
    total_items = 0
    
    for product in products:
        product_inventory = []
        
        for store in stores:
            # Different quantities per store type (distribuição realística MercadoLibre Brasil)
            quantity = {
                "MELI-CD-SP": 800,      # Centro principal SP - maior estoque
                "MELI-CD-RJ": 500,      # Centro regional RJ
                "MELI-CD-BH": 300,      # Centro regional BH
                "MELI-FC-CP": 400,      # Fulfillment Campinas
                "MELI-HUB-ZS-SP": 100,  # Hub última milha
                "MELI-ME-FL": 50,       # Ponto MercadoEnvios
                "MELI-XD-GRU": 200,     # Cross docking Guarulhos
                "MELI-SF-ABC": 150,     # Seller Flex ABC
                "MELI-PR-IGU": 30,      # Ponto de retirada shopping
                "MELI-CL-BSB": 250      # Centro logístico Brasília
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
            
            print(f"  ✓ {product['name'][:40]}... @ {store['name']}: {quantity} unidades")
        
        inventory_data[product["name"]] = product_inventory
    
    print()
    print("=" * 70)
    print("✅ INICIALIZAÇÃO COMPLETA!")
    print("=" * 70)
    print(f"\n📊 Resumo:")
    print(f"  • Produtos criados: {len(products)}")
    print(f"  • Centros de distribuição: {len(stores)}")
    print(f"  • Total de itens no inventário: {total_items}")
    print(f"  • Handlers de evento: {event_bus.get_handler_count()}")
    
    # Save IDs to file for reference
    print(f"\n💾 Salvando dados de referência...")
    with open("sample_data_ids.txt", "w", encoding="utf-8") as f:
        f.write("DADOS DE AMOSTRA - MERCADOLIBRE BRASIL\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("PRODUTOS:\n")
        for product in products:
            f.write(f"  {product['sku']}: {product['id']}\n")
        
        f.write("\nCENTROS DE DISTRIBUIÇÃO:\n")
        for store in stores:
            f.write(f"  {store['code']}: {store['id']}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("EXEMPLOS DE API:\n")
        f.write("=" * 70 + "\n\n")
        
        first_product = products[0]
        first_store = stores[0]
        
        f.write("# Verificar estoque:\n")
        f.write(f"GET /api/v1/inventory/products/{first_product['id']}/stores/{first_store['id']}\n\n")
        
        f.write("# Reservar estoque:\n")
        f.write(f"""POST /api/v1/inventory/reserve
{{
  "product_id": "{first_product['id']}",
  "store_id": "{first_store['id']}",
  "quantity": 2
}}
\n""")
    
    print(f"  ✓ Salvo em: sample_data_ids.txt\n")
    
    print("🚀 Próximos passos:")
    print("  1. Iniciar a API: python main.py")
    print("  2. Abrir Swagger UI: http://localhost:8000/swagger")
    print("  3. Usar os IDs em sample_data_ids.txt para testar\n")


if __name__ == "__main__":
    asyncio.run(initialize_sample_data())