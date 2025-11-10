# gestion/views/__init__.py

from .product_views import ProductListView, export_products_excel
from .movement_views import product_movement_view, ProductMovementListView, export_movements_excel, search_movements_live
from .supplier_views import (
    SupplierListView, 
    SupplierCreateView, 
    SupplierUpdateView
)
from .sale_views import (
    SaleListView,
    SaleDetailView,
    sale_create_view
)
from .user_views import (
    UserListView,
    UserCreateView,
    UserUpdateView,
    user_change_password,
    user_change_own_password,
    user_delete,
    export_users_excel
)
from .api_views import (
    get_product_stock_info, 
    get_all_zones,
    get_zones_by_warehouse,
    get_product_price,
    search_products_for_sale,
    process_sale
)
from .supplier_order_views import (
    SupplierOrderListView,
    SupplierOrderDetailView,
    supplier_order_create,
    supplier_order_add_items,
    supplier_order_receive,
    supplier_order_item_delete
)

__all__ = [
    'ProductListView', 'export_products_excel',
    'product_movement_view', 'ProductMovementListView', 'export_movements_excel', 'search_movements_live',
    'SupplierListView', 'SupplierCreateView', 'SupplierUpdateView',
    'SaleListView', 'SaleDetailView', 'sale_create_view',
    'UserListView', 'UserCreateView', 'UserUpdateView',
    'user_change_password', 'user_change_own_password', 'user_delete', 'export_users_excel',
    'get_product_stock_info', 'get_all_zones', 'get_zones_by_warehouse',
    'get_product_price', 'search_products_for_sale', 'process_sale',
    'SupplierOrderListView', 'SupplierOrderDetailView',
    'supplier_order_create', 'supplier_order_add_items',
    'supplier_order_receive', 'supplier_order_item_delete',
]