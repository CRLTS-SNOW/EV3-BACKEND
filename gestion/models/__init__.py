# gestion/models/__init__.py

# Modelos que ya teníamos
from .supplier import Supplier
from .warehouse import Warehouse
from .zone import Zone
from .product import Product
from .inventory import Inventory
from .product_movement import ProductMovement
from .product_supplier import ProductSupplier

# --- Modelos nuevos ---
from .user_profile import UserProfile
from .client import Client
from .sale import Sale
from .sale_item import SaleItem
from .supplier_order import SupplierOrder, SupplierOrderItem


__all__ = [
    'Supplier',
    'Warehouse',
    'Zone',
    'Product',
    'Inventory',
    'ProductMovement',
    'ProductSupplier',
    
    # --- Modelos nuevos ---
    'UserProfile',
    'Client',
    'Sale',
    'SaleItem',
    'SupplierOrder',
    'SupplierOrderItem',
]