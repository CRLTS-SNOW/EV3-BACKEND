from django.urls import path

# 1. Importaciones de Vistas de Producto
from .views.product_views import ProductListView, export_products_excel, search_products_live

# 2. Importaciones de Vistas de Proveedor
from .views.supplier_views import (
    SupplierListView, SupplierCreateView, SupplierUpdateView, 
    search_suppliers_live,         # <-- Importación para API de proveedores
    search_supplier_orders_live,  # <-- NUEVA importación para API de órdenes
    export_suppliers_excel
)

# 3. Importaciones de Vistas de Órdenes a Proveedores
from .views.supplier_order_views import (
    SupplierOrderListView, SupplierOrderDetailView, supplier_order_create, 
    supplier_order_add_items, supplier_order_receive, supplier_order_item_delete,
    search_supplier_orders_live_list, export_supplier_orders_excel
)

# ... (El resto de tus importaciones de sales, users, api, etc.)
from .views.movement_views import product_movement_view, ProductMovementListView, export_movements_excel, search_movements_live
from .views.sale_views import SaleListView, SaleDetailView, sale_create_view, search_sales_live, export_sales_excel
from .views.user_views import (
    UserListView, UserCreateView, UserUpdateView, 
    user_change_password, user_change_own_password, user_delete, search_users_live, export_users_excel
)
from .views.api_views import (
    get_product_stock_info, get_all_zones, get_zones_by_warehouse, 
    get_product_price, search_products_for_sale, process_sale, add_product_to_order, get_order_items
)

urlpatterns = [
    # --- Productos ---
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/export/', export_products_excel, name='export_products_excel'),
    path('api/search-products/', search_products_live, name='api_search_products_live'),
    
    # --- Movimientos ---
    path('movements/', product_movement_view, name='product_movement'),
    path('movements/list/', ProductMovementListView.as_view(), name='movement_list'),
    path('movements/export/', export_movements_excel, name='export_movements_excel'),
    path('api/search-movements/', search_movements_live, name='api_search_movements_live'),

    # --- Proveedores ---
    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/new/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/export/', export_suppliers_excel, name='export_suppliers_excel'),
    
    # --- Órdenes a Proveedores ---
    path('supplier-orders/', SupplierOrderListView.as_view(), name='supplier_order_list'),
    path('supplier-orders/new/', supplier_order_create, name='supplier_order_create'),
    path('supplier-orders/<int:pk>/', SupplierOrderDetailView.as_view(), name='supplier_order_detail'),
    path('supplier-orders/<int:pk>/add-items/', supplier_order_add_items, name='supplier_order_add_items'),
    path('supplier-orders/<int:pk>/receive/', supplier_order_receive, name='supplier_order_receive'),
    path('supplier-orders/<int:order_pk>/item/<int:item_pk>/delete/', supplier_order_item_delete, name='supplier_order_item_delete'),
    path('supplier-orders/export/', export_supplier_orders_excel, name='export_supplier_orders_excel'),

    # --- Ventas ---
    path('sales/', SaleListView.as_view(), name='sale_list'),
    path('sales/new/', sale_create_view, name='sale_create'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale_detail'),
    path('sales/export/', export_sales_excel, name='export_sales_excel'),
    
    # --- Usuarios ---
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/new/', UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/password/', user_change_password, name='user_change_password'),
    path('users/my-password/', user_change_own_password, name='user_change_own_password'),
    path('users/<int:pk>/delete/', user_delete, name='user_delete'),
    path('users/export/', export_users_excel, name='export_users_excel'),

    # --- Rutas de API (AJAX) ---
    
    # Rutas para Live Search (¡Aquí están las nuevas!)
    path('api/search-suppliers/', search_suppliers_live, name='api_search_suppliers_live'),
    path('api/search-supplier-orders/', search_supplier_orders_live, name='api_search_supplier_orders_live'),
    path('api/search-supplier-orders-list/', search_supplier_orders_live_list, name='api_search_supplier_orders_live_list'),
    path('api/search-sales/', search_sales_live, name='api_search_sales_live'),
    path('api/search-users/', search_users_live, name='api_search_users_live'),

    # Rutas API existentes
    path('api/product-stock/<int:product_id>/', get_product_stock_info, name='api_get_product_stock'),
    path('api/all-zones/', get_all_zones, name='api_get_all_zones'),
    path('api/zones-by-warehouse/<int:warehouse_id>/', get_zones_by_warehouse, name='api_get_zones_by_warehouse'),
    path('api/product-price/<int:product_id>/', get_product_price, name='api_get_product_price'),
    path('api/search-products-sale/', search_products_for_sale, name='api_search_products_sale'),
    path('api/process-sale/', process_sale, name='api_process_sale'),
    path('api/orders/<int:order_pk>/add-product/', add_product_to_order, name='api_add_product_to_order'),
    path('api/orders/<int:order_pk>/items/', get_order_items, name='api_get_order_items'),
]