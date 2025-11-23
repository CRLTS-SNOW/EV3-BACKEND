# gestion/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Product, Supplier, UserProfile, ProductMovement, 
    Sale, SaleItem, SupplierOrder, SupplierOrderItem,
    Client, Warehouse, Zone, Inventory, ProductSupplier
)

class ProductSerializer(serializers.ModelSerializer):
    total_stock = serializers.ReadOnlyField()
    stock_actual = serializers.ReadOnlyField(source='total_quantity')
    alerta_bajo_stock = serializers.ReadOnlyField()
    alerta_por_vencer = serializers.ReadOnlyField()
    supplier_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'ean_upc', 'name', 'descripcion', 'categoria', 
            'marca', 'modelo', 'uom_compra', 'uom_venta', 'factor_conversion',
            'costo_estandar', 'costo_promedio', 'precio_venta', 'impuesto_iva',
            'stock_minimo', 'stock_maximo', 'punto_reorden', 'perishable',
            'control_por_lote', 'control_por_serie', 'imagen_url', 
            'ficha_tecnica_url', 'is_active', 'created_at', 'updated_at',
            'total_stock', 'stock_actual', 'alerta_bajo_stock', 'alerta_por_vencer', 'supplier_name'
        ]
        read_only_fields = ['costo_promedio', 'total_stock', 'stock_actual', 'alerta_bajo_stock', 'alerta_por_vencer']
    
    def get_supplier_name(self, obj):
        # OPTIMIZACIÓN: Usar select_related en el queryset en lugar de hacer consulta aquí
        # Si supplier_preferente está en prefetch, usar eso
        if hasattr(obj, '_prefetched_objects_cache') and 'supplier_preferente' in obj._prefetched_objects_cache:
            supplier = obj._prefetched_objects_cache['supplier_preferente']
        else:
            supplier = obj.supplier_preferente
        return supplier.nombre_display if supplier else None

class SupplierSerializer(serializers.ModelSerializer):
    nombre_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'rut_nif', 'razon_social', 'nombre_fantasia', 'email',
            'telefono', 'sitio_web', 'direccion', 'ciudad', 'pais',
            'condiciones_pago', 'moneda', 'contacto_principal_nombre',
            'contacto_principal_email', 'contacto_principal_telefono',
            'estado', 'observaciones', 'is_active', 'created_at', 'updated_at',
            'nombre_display'
        ]

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'address', 'is_active']

class ZoneSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Zone
        fields = ['id', 'name', 'warehouse', 'warehouse_name', 'is_active']

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'zone', 'zone_name', 'quantity']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'nombres',
            'apellidos', 'phone', 'role', 'role_display', 'estado',
            'warehouse', 'warehouse_name', 'area', 'observaciones',
            'mfa_habilitado', 'ultimo_acceso', 'sesiones_activas', 'is_active', 'nombre_completo',
            'photo'
        ]
        read_only_fields = ['ultimo_acceso', 'sesiones_activas']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login', 'profile'
        ]

class ProductMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    origin_zone_name = serializers.CharField(source='origin_zone.name', read_only=True, allow_null=True)
    destination_zone_name = serializers.CharField(source='destination_zone.name', read_only=True, allow_null=True)
    supplier_name = serializers.CharField(source='supplier.razon_social', read_only=True, allow_null=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    user_name = serializers.CharField(source='performed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = ProductMovement
        fields = [
            'id', 'product', 'product_name', 'product_sku', 
            'origin_zone', 'origin_zone_name',
            'destination_zone', 'destination_zone_name',
            'supplier', 'supplier_name',
            'warehouse', 'warehouse_name',
            'quantity', 'cantidad',
            'fecha', 'tipo', 'movement_type', 
            'lote', 'serie', 'fecha_vencimiento',
            'doc_referencia', 'motivo', 'reason',
            'observaciones',
            'performed_by', 'user_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone', 'address', 'rut_nif', 'is_active']

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'price_at_sale', 'subtotal'
        ]
    
    def get_subtotal(self, obj):
        """Calcula el subtotal del item"""
        subtotal = obj.quantity * obj.price_at_sale
        # Convertir Decimal a float para JSON
        return float(subtotal)

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True, allow_null=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'client', 'client_name', 'user', 'user_name',
            'total_amount', 'sale_date', 'items'
        ]

class SupplierOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    
    class Meta:
        model = SupplierOrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'subtotal'
        ]

class SupplierOrderSerializer(serializers.ModelSerializer):
    items = SupplierOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.nombre_display', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True, allow_null=True)
    zone_name = serializers.CharField(source='zone.name', read_only=True, allow_null=True)
    requested_by_name = serializers.CharField(source='requested_by.username', read_only=True)
    
    class Meta:
        model = SupplierOrder
        fields = [
            'id', 'supplier', 'supplier_name', 'warehouse', 'warehouse_name',
            'zone', 'zone_name', 'order_date', 'expected_delivery_date',
            'received_date', 'status', 'total_amount', 'requested_by',
            'requested_by_name', 'observaciones', 'items'
        ]

class ProductSupplierSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    supplier_name = serializers.CharField(source='supplier.razon_social', read_only=True)
    
    class Meta:
        model = ProductSupplier
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'supplier', 'supplier_name',
            'costo', 'lead_time_dias', 'min_lote', 'descuento_pct', 'preferente',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

