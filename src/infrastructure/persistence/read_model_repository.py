"""Read Model Repository for optimized queries"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID


class ReadModelRepository:
    """
    Repository for read models (CQRS read side).
    
    Maintains denormalized views optimized for queries.
    Updated by event handlers.
    """
    
    def __init__(self, storage_path: str = "data/read_models"):
        """
        Initialize repository.
        
        Args:
            storage_path: Directory to store read models
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._inventory_file = self.storage_path / "inventory.json"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the inventory file exists"""
        if not self._inventory_file.exists():
            self._inventory_file.write_text("{}")
    
    def _load_inventory(self) -> Dict:
        """Load inventory from file"""
        with open(self._inventory_file, 'r') as f:
            return json.load(f)
    
    def _save_inventory(self, inventory: Dict):
        """Save inventory to file"""
        with open(self._inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)
    
    def _make_key(self, product_id: UUID, store_id: UUID) -> str:
        """Create key for inventory lookup"""
        return f"{product_id}:{store_id}"
    
    def update_stock(
        self, 
        product_id: UUID, 
        store_id: UUID,
        available: int,
        reserved: int
    ):
        """
        Update stock levels in read model.
        
        Args:
            product_id: Product identifier
            store_id: Store identifier
            available: Available quantity
            reserved: Reserved quantity
        """
        inventory = self._load_inventory()
        key = self._make_key(product_id, store_id)
        
        inventory[key] = {
            'product_id': str(product_id),
            'store_id': str(store_id),
            'available': available,
            'reserved': reserved,
            'total': available + reserved
        }
        
        self._save_inventory(inventory)
    
    def get_stock(
        self, 
        product_id: UUID, 
        store_id: UUID
    ) -> Optional[Dict]:
        """
        Get stock for a specific product and store.
        
        Args:
            product_id: Product identifier
            store_id: Store identifier
        
        Returns:
            Stock information or None if not found
        """
        inventory = self._load_inventory()
        key = self._make_key(product_id, store_id)
        return inventory.get(key)
    
    def get_product_inventory(self, product_id: UUID) -> List[Dict]:
        """
        Get inventory for a product across all stores.
        
        Args:
            product_id: Product identifier
        
        Returns:
            List of stock information for each store
        """
        inventory = self._load_inventory()
        product_id_str = str(product_id)
        
        results = []
        for key, data in inventory.items():
            if data['product_id'] == product_id_str:
                results.append(data)
        
        return results
    
    def check_availability(
        self, 
        product_id: UUID, 
        store_id: UUID,
        required_quantity: int
    ) -> bool:
        """
        Check if required quantity is available.
        
        Args:
            product_id: Product identifier
            store_id: Store identifier
            required_quantity: Required quantity
        
        Returns:
            True if available, False otherwise
        """
        stock = self.get_stock(product_id, store_id)
        if not stock:
            return False
        
        return stock['available'] >= required_quantity
