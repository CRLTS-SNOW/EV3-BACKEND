# gestion/views/__init__.py

# Solo importar las vistas REST que se usan
from .rest_views import (
    ProductViewSet, SupplierViewSet, UserViewSet,
    ProductMovementViewSet, SaleViewSet, SupplierOrderViewSet,
    ClientViewSet, WarehouseViewSet, ZoneViewSet,
    current_user, api_login, api_logout, reset_password, reset_password_confirm
)

__all__ = [
    'ProductViewSet', 'SupplierViewSet', 'UserViewSet',
    'ProductMovementViewSet', 'SaleViewSet', 'SupplierOrderViewSet',
    'ClientViewSet', 'WarehouseViewSet', 'ZoneViewSet',
    'current_user', 'api_login', 'api_logout', 'reset_password', 'reset_password_confirm',
]