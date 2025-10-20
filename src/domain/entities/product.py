"""Product entity - Represents a product in the inventory system"""
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Product:
    """
    Product entity representing an item in the inventory.
    
    Attributes:
        id: Unique identifier for the product
        name: Product name
        sku: Stock Keeping Unit - unique product code
    """
    id: UUID
    name: str
    sku: str
    
    def __post_init__(self):
        """Validate product attributes"""
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if not self.sku or not self.sku.strip():
            raise ValueError("Product SKU cannot be empty")
