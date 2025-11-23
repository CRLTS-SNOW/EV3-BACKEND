# gestion/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.rest_views import (
    ProductViewSet, SupplierViewSet, UserViewSet,
    ProductMovementViewSet, SaleViewSet, SupplierOrderViewSet,
    ClientViewSet, WarehouseViewSet, ZoneViewSet, current_user, api_login, api_logout, reset_password, reset_password_confirm
)
from .views.api_views import search_products_for_sale, get_all_products_for_sale

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'users', UserViewSet, basename='user')
router.register(r'movements', ProductMovementViewSet, basename='movement')
router.register(r'sales', SaleViewSet, basename='sale')
router.register(r'supplier-orders', SupplierOrderViewSet, basename='supplier-order')
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'zones', ZoneViewSet, basename='zone')

urlpatterns = [
    path('', include(router.urls)),
    path('current-user/', current_user, name='api_current_user'),
    path('login/', api_login, name='api_login'),
    path('logout/', api_logout, name='api_logout'),
    path('reset-password/', reset_password, name='api_reset_password'),
    path('reset-password-confirm/', reset_password_confirm, name='api_reset_password_confirm'),
    path('users/change-own-password/', UserViewSet.as_view({'post': 'change_own_password'}), name='api_change_own_password'),
    path('search-products-for-sale/', search_products_for_sale, name='api_search_products_for_sale'),
    path('all-products-for-sale/', get_all_products_for_sale, name='api_all_products_for_sale'),
]

