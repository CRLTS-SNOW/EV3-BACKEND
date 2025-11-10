# gestion/models/__init__.py

# Modelos que ya teníamos
from .supplier import Supplier
from .warehouse import Warehouse
from .zone import Zone
from .product import Product
from .inventory import Inventory
from .product_movement import ProductMovement

# --- Modelos nuevos ---
from .user_profile import UserProfile # <-- Este archivo ahora SÍ existe
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
    
    # --- Modelos nuevos ---
    'UserProfile',
    'Client',
    'Sale',
    'SaleItem',
    'SupplierOrder',
    'SupplierOrderItem',
]