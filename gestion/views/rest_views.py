# gestion/views/rest_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Sum, Prefetch
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.contrib.auth import logout as django_logout
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
from decimal import Decimal
import json

from ..models import (
    Product, Supplier, UserProfile, ProductMovement,
    Sale, SaleItem, SupplierOrder, SupplierOrderItem,
    Client, Warehouse, Zone, Inventory, ProductSupplier
)
from ..serializers import (
    ProductSerializer, SupplierSerializer, UserSerializer, UserProfileSerializer,
    ProductMovementSerializer, SaleSerializer, SaleItemSerializer,
    SupplierOrderSerializer, SupplierOrderItemSerializer,
    ClientSerializer, WarehouseSerializer, ZoneSerializer, InventorySerializer,
    ProductSupplierSerializer
)
from ..auth_utils import is_admin, is_bodega_or_admin
from ..forms.product_forms import ProductForm
from ..forms.supplier_forms import SupplierForm
from ..forms.user_forms import UserCreateForm, UserUpdateForm, UserPasswordChangeForm
from ..forms.movement_forms import ProductMovementForm
from ..forms.supplier_order_forms import SupplierOrderForm
from ..pagination import OptimizedPageNumberPagination


# ==================== PRODUCTOS ====================
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OptimizedPageNumberPagination
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # OPTIMIZACIÓN CRÍTICA: Prefetch con Prefetch object para optimizar stock
        # Solo traer campos necesarios para reducir memoria y mejorar velocidad
        stock_prefetch = Prefetch(
            'stock',
            queryset=Inventory.objects.select_related('zone', 'zone__warehouse').only(
                'product_id', 'quantity', 'zone_id', 'zone__name', 'zone__warehouse__name'
            )
        )
        queryset = queryset.prefetch_related(stock_prefetch)
        
        # OPTIMIZACIÓN: Anotar stock total usando agregación directa (más rápido que Subquery)
        # Los índices compuestos en Inventory mejoran significativamente esta consulta
        queryset = queryset.annotate(
            total_stock=Coalesce(Sum('stock__quantity'), 0)
        )
        
        search_query = self.request.query_params.get('q', None)
        if search_query:
            # OPTIMIZACIÓN: Índices en name, sku, categoria mejoran estas búsquedas
            # Los índices compuestos (is_active, name) aceleran búsquedas en productos activos
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(categoria__icontains=search_query)
            )
        
        sort_by = self.request.query_params.get('sort', 'name')
        sort_options = {
            'name': 'name',
            '-name': '-name',
            'stock': 'total_stock',
            '-stock': '-total_stock',
            'price': 'precio_venta',
            '-price': '-precio_venta',
            'sku': 'sku',
            '-sku': '-sku',
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        # Preparar datos del formulario
        form_data = request.data.copy()
        
        # Si no se proporciona SKU, se generará automáticamente en el modelo
        if 'sku' in form_data and not form_data.get('sku'):
            del form_data['sku']
        
        form = ProductForm(form_data)
        if form.is_valid():
            product = form.save()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        product = self.get_object()
        
        # Preparar datos del formulario
        form_data = request.data.copy()
        
        # No permitir cambiar el SKU al editar
        if 'sku' in form_data:
            del form_data['sku']
        
        form = ProductForm(form_data, instance=product)
        if form.is_valid():
            product = form.save()
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== PROVEEDORES ====================
class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(razon_social__icontains=search_query) |
                Q(nombre_fantasia__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(rut_nif__icontains=search_query)
            )
        
        sort_by = self.request.query_params.get('sort', 'razon_social')
        sort_options = {
            'name': 'razon_social',
            '-name': '-razon_social',
            'razon_social': 'razon_social',
            '-razon_social': '-razon_social',
            'email': 'email',
            '-email': '-email',
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('razon_social')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        form = SupplierForm(request.data)
        if form.is_valid():
            supplier = form.save()
            serializer = self.get_serializer(supplier)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = self.get_object()
        form = SupplierForm(request.data, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            serializer = self.get_serializer(supplier)
            return Response(serializer.data)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get', 'post', 'put', 'delete'], url_path='products')
    def products(self, request, pk=None):
        """Gestionar productos asociados al proveedor"""
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        supplier = self.get_object()
        
        if request.method == 'GET':
            # Listar productos asociados
            product_suppliers = ProductSupplier.objects.filter(supplier=supplier).select_related('product')
            serializer = ProductSupplierSerializer(product_suppliers, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Crear nueva relación producto-proveedor
            data = request.data.copy()
            data['supplier'] = supplier.id
            
            # Validar preferente: si se marca como preferente, quitar preferente de otros
            if data.get('preferente') in [True, 'true', 'True', '1', 1]:
                product_id = data.get('product')
                if product_id:
                    ProductSupplier.objects.filter(
                        product_id=product_id,
                        preferente=True
                    ).update(preferente=False)
            
            serializer = ProductSupplierSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PUT':
            # Actualizar relación existente
            product_id = request.data.get('product')
            if not product_id:
                return Response({'error': 'product es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                product_supplier = ProductSupplier.objects.get(supplier=supplier, product_id=product_id)
            except ProductSupplier.DoesNotExist:
                return Response({'error': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            
            # Validar preferente: si se marca como preferente, quitar preferente de otros
            if request.data.get('preferente') in [True, 'true', 'True', '1', 1]:
                ProductSupplier.objects.filter(
                    product_id=product_id,
                    preferente=True
                ).exclude(pk=product_supplier.pk).update(preferente=False)
            
            serializer = ProductSupplierSerializer(product_supplier, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            # Eliminar relación
            product_id = request.data.get('product')
            if not product_id:
                return Response({'error': 'product es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                product_supplier = ProductSupplier.objects.get(supplier=supplier, product_id=product_id)
                product_supplier.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ProductSupplier.DoesNotExist:
                return Response({'error': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)


# ==================== USUARIOS ====================
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not (is_admin(self.request.user) or self.request.user.is_superuser):
            return User.objects.none()
        
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        sort_by = self.request.query_params.get('sort', 'username')
        sort_options = {
            'username': 'username',
            '-username': '-username',
            'email': 'email',
            '-email': '-email',
            'first_name': 'first_name',
            '-first_name': '-first_name',
            'last_name': 'last_name',
            '-last_name': '-last_name',
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('username')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        form = UserCreateForm(request.data)
        if form.is_valid():
            user = form.save()
            # Sincronizar con Firebase
            from ..firebase_service import sync_django_user_to_firebase
            password = form.cleaned_data.get('password')
            if user.email:
                sync_django_user_to_firebase(user, password=password, old_email=None)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        
        # Prevenir que el usuario admin cambie su rol
        if user.username == 'admin' and 'role' in request.data:
            if request.data.get('role') != getattr(user.profile, 'role', 'admin'):
                return Response(
                    {'error': 'El usuario admin no puede cambiar su rol'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Guardar email anterior ANTES de actualizar (normalizado)
        old_email = user.email.strip().lower() if user.email else None
        
        # Preparar datos para el formulario
        form_data = request.data.copy()
        
        # Si es el usuario admin, forzar el rol a 'admin' para evitar cambios
        if user.username == 'admin':
            form_data['role'] = 'admin'
        
        # Manejar campos booleanos que pueden venir como strings
        if 'is_active' in form_data:
            form_data['is_active'] = form_data['is_active'] in [True, 'true', 'True', '1', 1]
        else:
            form_data['is_active'] = user.is_active
        
        if 'mfa_habilitado' in form_data:
            form_data['mfa_habilitado'] = form_data['mfa_habilitado'] in [True, 'true', 'True', '1', 1]
        
        form = UserUpdateForm(form_data, instance=user)
        if form.is_valid():
            try:
                user = form.save()
                new_email = user.email.strip().lower() if user.email else None
                
                # Sincronizar automáticamente con Firebase
                from ..firebase_service import sync_django_user_to_firebase, get_firebase_user_by_email
                if user.email:
                    # Normalizar emails para comparación
                    old_email_normalized = old_email.strip().lower() if old_email else None
                    new_email_normalized = new_email.strip().lower() if new_email else None
                    
                    # Verificar si el email cambió
                    email_changed = old_email_normalized and old_email_normalized != new_email_normalized
                    
                    # Si el email cambió, verificar si el nuevo email ya existe en Firebase
                    if email_changed:
                        existing_firebase_user = get_firebase_user_by_email(new_email_normalized)
                        if existing_firebase_user:
                            # Buscar el usuario actual en Firebase por el email anterior
                            old_firebase_user = get_firebase_user_by_email(old_email_normalized)
                            # Solo rechazar si el email existe y pertenece a OTRO usuario diferente
                            if not old_firebase_user or existing_firebase_user.uid != old_firebase_user.uid:
                                return Response(
                                    {'error': f'El email {new_email} ya está en uso por otro usuario en Firebase'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            # Si es el mismo usuario, permitir el cambio (puede pasar si hay inconsistencias)
                    
                    # Sincronizar con Firebase (esto manejará correctamente el caso cuando el email no cambió)
                    firebase_result = sync_django_user_to_firebase(user, password=None, old_email=old_email)
                    if not firebase_result:
                        # Si Firebase no está configurado o hay un error, continuar pero mostrar advertencia en DEBUG
                        if settings.DEBUG:
                            print(f"ADVERTENCIA: No se pudo sincronizar usuario {user.username} con Firebase")
                
                serializer = self.get_serializer(user)
                return Response(serializer.data)
            except Exception as e:
                error_msg = str(e)
                # Si el error menciona EMAIL_EXISTS, devolver un mensaje más claro
                if 'EMAIL_EXISTS' in error_msg or 'email already exists' in error_msg.lower():
                    return Response(
                        {'error': f'El email {new_email} ya está en uso por otro usuario'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    {'error': f'Error al guardar: {error_msg}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Cambiar contraseña de un usuario (solo admin)"""
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        form = UserPasswordChangeForm(request.data, user=user, is_own_password=False)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            from ..firebase_service import get_firebase_user_by_email, update_firebase_user
            if user.email:
                firebase_user = get_firebase_user_by_email(user.email)
                if firebase_user:
                    result = update_firebase_user(firebase_user.uid, password=new_password)
                    if result:
                        return Response({'message': 'Contraseña actualizada exitosamente en Firebase'})
                    else:
                        return Response({'error': 'Error al actualizar la contraseña en Firebase'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'error': 'Usuario no encontrado en Firebase'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'El usuario no tiene email configurado'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='change-own-password')
    def change_own_password(self, request):
        """Permite que un usuario cambie su propia contraseña"""
        user = request.user
        form = UserPasswordChangeForm(request.data, user=user, is_own_password=True)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            from ..firebase_service import get_firebase_user_by_email, update_firebase_user
            if user.email:
                firebase_user = get_firebase_user_by_email(user.email)
                if firebase_user:
                    result = update_firebase_user(firebase_user.uid, password=new_password)
                    if result:
                        return Response({'message': 'Tu contraseña ha sido actualizada exitosamente en Firebase'})
                    else:
                        return Response({'error': 'Error al actualizar la contraseña en Firebase'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'error': 'Usuario no encontrado en Firebase'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'No tienes email configurado'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def delete_user(self, request, pk=None):
        if not (is_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        email = user.email
        username = user.username
        
        # Eliminar de Firebase si existe
        if email:
            from ..firebase_service import get_firebase_user_by_email, delete_firebase_user
            firebase_user = get_firebase_user_by_email(email)
            if firebase_user:
                delete_firebase_user(firebase_user.uid)
        
        user.delete()
        return Response({'message': f'Usuario {username} eliminado exitosamente'})


# ==================== MOVIMIENTOS ====================
class ProductMovementViewSet(viewsets.ModelViewSet):
    queryset = ProductMovement.objects.all().select_related(
        'product', 'origin_zone', 'destination_zone', 'supplier', 'warehouse', 'performed_by'
    )
    serializer_class = ProductMovementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(product__sku__icontains=search_query)
            )
        
        return queryset.order_by('-fecha')
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        # Convertir request.data a dict si es necesario para que el formulario lo lea correctamente
        data = dict(request.data) if hasattr(request.data, 'items') else request.data
        form = ProductMovementForm(data)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.performed_by = request.user
            
            # Si no hay fecha, usar la fecha actual
            if not movement.fecha:
                from django.utils import timezone
                movement.fecha = timezone.now()
            
            # Guardar movimiento
            movement.save()
            
            # Actualizar inventario según el tipo de movimiento
            try:
                with transaction.atomic():
                    cantidad = movement.cantidad
                    product = movement.product
                    
                    if movement.tipo == 'ingreso':
                        # Ingreso: agregar a zona destino
                        if movement.destination_zone:
                            inventory, created = Inventory.objects.get_or_create(
                                product=product,
                                zone=movement.destination_zone,
                                defaults={'quantity': 0}
                            )
                            inventory.quantity += int(cantidad)
                            inventory.save()
                    
                    elif movement.tipo == 'salida':
                        # Salida: restar de zona origen o destino
                        zone = movement.origin_zone or movement.destination_zone
                        if zone:
                            try:
                                inventory = Inventory.objects.get(product=product, zone=zone)
                                if inventory.quantity < int(cantidad):
                                    return Response({
                                        'error': f'Stock insuficiente. Disponible: {inventory.quantity}, Solicitado: {int(cantidad)}'
                                    }, status=status.HTTP_400_BAD_REQUEST)
                                inventory.quantity -= int(cantidad)
                                inventory.save()
                            except Inventory.DoesNotExist:
                                return Response({
                                    'error': f'No hay stock del producto en la zona seleccionada'
                                }, status=status.HTTP_400_BAD_REQUEST)
                    
                    elif movement.tipo == 'ajuste':
                        # Ajuste: establecer cantidad en zona destino
                        if movement.destination_zone:
                            inventory, created = Inventory.objects.get_or_create(
                                product=product,
                                zone=movement.destination_zone,
                                defaults={'quantity': 0}
                            )
                            inventory.quantity = int(cantidad)
                            inventory.save()
                    
                    elif movement.tipo == 'devolucion':
                        # Devolución: agregar a zona destino
                        if movement.destination_zone:
                            inventory, created = Inventory.objects.get_or_create(
                                product=product,
                                zone=movement.destination_zone,
                                defaults={'quantity': 0}
                            )
                            inventory.quantity += int(cantidad)
                            inventory.save()
                    
                    elif movement.tipo == 'transferencia':
                        # Transferencia: restar de origen, agregar a destino
                        if movement.origin_zone and movement.destination_zone:
                            # Restar de origen
                            try:
                                origin_inventory = Inventory.objects.get(product=product, zone=movement.origin_zone)
                                if origin_inventory.quantity < int(cantidad):
                                    return Response({
                                        'error': f'Stock insuficiente en zona origen. Disponible: {origin_inventory.quantity}, Solicitado: {int(cantidad)}'
                                    }, status=status.HTTP_400_BAD_REQUEST)
                                origin_inventory.quantity -= int(cantidad)
                                origin_inventory.save()
                            except Inventory.DoesNotExist:
                                return Response({
                                    'error': f'No hay stock del producto en la zona origen'
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            # Agregar a destino
                            destination_inventory, created = Inventory.objects.get_or_create(
                                product=product,
                                zone=movement.destination_zone,
                                defaults={'quantity': 0}
                            )
                            destination_inventory.quantity += int(cantidad)
                            destination_inventory.save()
            
            except Exception as e:
                import traceback
                print(f"Error al actualizar inventario: {str(e)}")
                print(traceback.format_exc())
                return Response({
                    'error': f'Error al actualizar inventario: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serializer = self.get_serializer(movement)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== VENTAS ====================
class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().select_related('client', 'user').prefetch_related('items__product')
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            queryset = super().get_queryset()
            params = self.request.query_params
            
            # Filtro de búsqueda por texto (ID, cliente o usuario)
            search_query = params.get('q', None)
            if search_query:
                if search_query.isdigit():
                    queryset = queryset.filter(id=search_query)
                else:
                    queryset = queryset.filter(
                        Q(client__name__icontains=search_query) |
                        Q(user__username__icontains=search_query)
                    )
            
            # Filtro por cliente
            client_id = params.get('client_id', None)
            if client_id:
                queryset = queryset.filter(client_id=client_id)
            
            # Filtro por usuario
            user_id = params.get('user_id', None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)
            
            # Filtro por rango de fechas
            date_from = params.get('date_from', None)
            date_to = params.get('date_to', None)
            if date_from:
                queryset = queryset.filter(sale_date__gte=date_from)
            if date_to:
                # Agregar 1 día para incluir todo el día 'date_to'
                from datetime import datetime, timedelta
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                    date_to_obj = date_to_obj + timedelta(days=1)
                    queryset = queryset.filter(sale_date__lt=date_to_obj.strftime('%Y-%m-%d'))
                except:
                    queryset = queryset.filter(sale_date__lte=date_to)
            
            # Filtro por rango de total
            total_min = params.get('total_min', None)
            total_max = params.get('total_max', None)
            if total_min:
                try:
                    queryset = queryset.filter(total_amount__gte=Decimal(total_min))
                except:
                    pass
            if total_max:
                try:
                    queryset = queryset.filter(total_amount__lte=Decimal(total_max))
                except:
                    pass
            
            # Ordenamiento
            order_by = params.get('order_by', '-sale_date')  # Por defecto: más reciente primero
            
            # Validar y aplicar ordenamiento
            valid_orders = {
                '-sale_date': '-sale_date',  # Más reciente primero (por defecto)
                'sale_date': 'sale_date',    # Más antiguo primero
                '-total_amount': '-total_amount',  # Mayor precio primero
                'total_amount': 'total_amount',    # Menor precio primero
                '-id': '-id',  # ID más alto primero
                'id': 'id',    # ID más bajo primero
            }
            
            order_field = valid_orders.get(order_by, '-sale_date')
            return queryset.order_by(order_field)
        except Exception as e:
            import traceback
            print(f"Error en get_queryset de SaleViewSet: {str(e)}")
            print(traceback.format_exc())
            # Retornar queryset vacío en caso de error
            return Sale.objects.none()
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error al listar ventas: {str(e)}")
            print(f"Traceback: {error_trace}")
            return Response({
                'error': f'Error al cargar ventas: {str(e)}',
                'detail': error_trace if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or request.user.profile.role == 'ventas' or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        client_id = data.get('client_id')
        cart = data.get('cart', [])
        
        if not cart:
            return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener zona de ventas
        from ..views.api_views import get_sales_zone
        sales_zone = get_sales_zone()
        if not sales_zone:
            # Si no hay zona de ventas, usar la primera zona activa disponible
            from ..models import Zone
            sales_zone = Zone.objects.filter(is_active=True).first()
            if not sales_zone:
                return Response({
                    'error': 'No hay zonas activas configuradas. Por favor, configure al menos una zona antes de realizar ventas.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Validar stock
        errors = []
        for item in cart:
            product_id = item.get('id')
            quantity = item.get('quantity', 0)
            
            if not product_id:
                errors.append("Producto sin ID válido en el carrito")
                continue
                
            if quantity <= 0:
                errors.append(f"Cantidad inválida para el producto ID {product_id}")
                continue
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                try:
                    inventory = Inventory.objects.get(product=product, zone=sales_zone)
                    if inventory.quantity < quantity:
                        errors.append(
                            f"Stock insuficiente para {product.name}. "
                            f"Disponible: {inventory.quantity}, Solicitado: {quantity}"
                        )
                except Inventory.DoesNotExist:
                    errors.append(f"No hay stock de {product.name} (SKU: {product.sku}) en la zona de ventas '{sales_zone.name}'")
            except Product.DoesNotExist:
                errors.append(f"Producto con ID {product_id} no encontrado o inactivo")
            except Exception as e:
                errors.append(f"Error al validar producto ID {product_id}: {str(e)}")
        
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Procesar venta
        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    client_id=client_id if client_id else None,
                    user=request.user,
                    total_amount=Decimal('0.00')
                )
                
                total_amount = Decimal('0.00')
                
                for item in cart:
                    product_id = item.get('id')
                    quantity = item.get('quantity', 0)
                    
                    if not product_id:
                        raise ValueError("Producto sin ID válido en el carrito")
                    
                    if quantity <= 0:
                        raise ValueError(f"Cantidad inválida para el producto ID {product_id}")
                    
                    try:
                        product = Product.objects.get(id=product_id, is_active=True)
                    except Product.DoesNotExist:
                        raise ValueError(f"Producto con ID {product_id} no encontrado o inactivo")
                    
                    try:
                        inventory = Inventory.objects.get(product=product, zone=sales_zone)
                    except Inventory.DoesNotExist:
                        raise ValueError(f"No hay stock de {product.name} (SKU: {product.sku}) en la zona de ventas '{sales_zone.name}'")
                    
                    # Validar stock antes de procesar
                    if inventory.quantity < quantity:
                        raise ValueError(
                            f"Stock insuficiente para {product.name}. "
                            f"Disponible: {inventory.quantity}, Solicitado: {quantity}"
                        )
                    
                    # Convertir precio a Decimal de forma segura
                    if product.precio_venta is not None:
                        sale_price = Decimal(str(product.precio_venta))
                    else:
                        sale_price = Decimal('0.00')
                    
                    item_price = sale_price * Decimal(str(quantity))
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        price_at_sale=sale_price
                    )
                    
                    # Descontar stock
                    inventory.quantity -= quantity
                    inventory.save()
                    
                    total_amount += item_price
                
                sale.total_amount = total_amount
                sale.save()
            
            serializer = self.get_serializer(sale)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            # Errores de validación (stock, productos no encontrados, etc.)
            return Response({'error': str(e), 'errors': [str(e)]}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_message = str(e)
            
            # Log del error para debugging
            print(f"ERROR al procesar venta: {error_message}")
            print(f"Traceback completo:")
            print(error_trace)
            
            # Mensaje de error más amigable
            if 'DoesNotExist' in str(type(e)):
                error_message = f"Error: {error_message}"
            elif 'IntegrityError' in str(type(e)):
                error_message = "Error de integridad en la base de datos. Por favor, intente nuevamente."
            elif 'ValidationError' in str(type(e)):
                error_message = f"Error de validación: {error_message}"
            
            return Response({
                'error': error_message,
                'errors': [error_message],
                'detail': error_trace if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== ÓRDENES A PROVEEDORES ====================
class SupplierOrderViewSet(viewsets.ModelViewSet):
    queryset = SupplierOrder.objects.all().select_related('supplier', 'warehouse', 'zone', 'requested_by').prefetch_related('items__product')
    serializer_class = SupplierOrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q', None)
        order_status = self.request.query_params.get('status', None)
        
        if order_status:
            queryset = queryset.filter(status=order_status)
        
        if search_query:
            if search_query.isdigit():
                queryset = queryset.filter(id=search_query)
            else:
                queryset = queryset.filter(
                    Q(supplier__razon_social__icontains=search_query) |
                    Q(supplier__nombre_fantasia__icontains=search_query)
                )
        
        return queryset.order_by('-order_date')
    
    def create(self, request, *args, **kwargs):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        form = SupplierOrderForm(request.data)
        if form.is_valid():
            order = form.save(commit=False)
            order.requested_by = request.user
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response({'error': 'No se pueden modificar órdenes que no están pendientes'}, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            return Response({'error': 'La cantidad debe ser mayor a 0'}, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        
        # Verificar que el producto pertenece al proveedor
        product_supplier = ProductSupplier.objects.filter(
            product=product,
            supplier=order.supplier
        ).first()
        
        if not product_supplier:
            return Response({'error': 'Este producto no pertenece al proveedor de la orden'}, status=status.HTTP_400_BAD_REQUEST)
        
        unit_price = product_supplier.costo if product_supplier.costo else product.precio_venta
        
        # Verificar si el producto ya está en la orden
        existing_item = SupplierOrderItem.objects.filter(order=order, product=product).first()
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.unit_price = unit_price
            existing_item.save()
            item = existing_item
        else:
            item = SupplierOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price
            )
        
        serializer = SupplierOrderItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response({'error': 'Solo se pueden recibir órdenes pendientes'}, status=status.HTTP_400_BAD_REQUEST)
        
        if order.items.count() == 0:
            return Response({'error': 'La orden no tiene items. Agrega productos antes de recibirla.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Procesar recepción de orden
        from django.utils import timezone
        try:
            with transaction.atomic():
                # Actualizar el estado de la orden
                order.status = 'RECEIVED'
                order.received_date = timezone.now()
                order.save()
                
                # Procesar cada item
                for item in order.items.select_related('product').all():
                    # Crear o actualizar inventario
                    inventory, created = Inventory.objects.get_or_create(
                        product=item.product,
                        zone=order.zone,
                        defaults={'quantity': 0}
                    )
                    inventory.quantity += item.quantity
                    inventory.save()
                    
                    # Crear movimiento de entrada
                    ProductMovement.objects.create(
                        product=item.product,
                        cantidad=item.quantity,
                        tipo='ingreso',
                        destination_zone=order.zone,
                        performed_by=request.user,
                        motivo=f"Recibo de orden #{order.id} de {order.supplier.razon_social if order.supplier else 'N/A'}",
                        fecha=timezone.now()
                    )
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='items/(?P<item_pk>[^/.]+)')
    def delete_item(self, request, pk=None, item_pk=None):
        if not (is_admin(request.user) or is_bodega_or_admin(request.user) or request.user.is_superuser):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        
        if order.status != 'PENDING':
            return Response({'error': 'No se pueden modificar órdenes que no están pendientes'}, status=status.HTTP_400_BAD_REQUEST)
        
        item = get_object_or_404(SupplierOrderItem, pk=item_pk, order=order)
        item.delete()
        
        return Response({'message': 'Item eliminado exitosamente'})


# ==================== CLIENTES ====================
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


# ==================== BODEGAS Y ZONAS ====================
class WarehouseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Warehouse.objects.filter(is_active=True)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]

class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Zone.objects.filter(is_active=True)
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]


# ==================== VISTAS DE API ADICIONALES ====================
@api_view(['GET'])
@permission_classes([])  # Permitir acceso sin autenticación para verificar estado
def current_user(request):
    """Devuelve información del usuario actual"""
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    else:
        # Devolver 401 en lugar de 403 cuando no hay usuario autenticado
        return Response(
            {'detail': 'Authentication credentials were not provided.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
@permission_classes([])  # Sin autenticación requerida para reset password
def reset_password(request):
    """API para restablecer contraseña usando Firebase"""
    email = request.data.get('email')
    
    if not email:
        return Response(
            {'error': 'El correo electrónico es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verificar si el email existe en la base de datos
    try:
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # Por seguridad, devolver mensaje genérico sin revelar si el correo existe o no
            return Response(
                {'error': 'Correo electrónico inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Excepción al verificar email: {e}")
        # Por seguridad, devolver mensaje genérico
        return Response(
            {'error': 'Correo electrónico inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from ..firebase_service import send_password_reset_email
        result = send_password_reset_email(email)
        
        if result.get('success'):
            return Response({
                'message': 'Se ha enviado un enlace de restablecimiento de contraseña a tu correo electrónico',
                'success': True
            })
        else:
            # Si Firebase falla, devolver mensaje genérico por seguridad
            error_msg = result.get('error', 'Error al enviar el correo de restablecimiento')
            if settings.DEBUG:
                print(f"DEBUG: Error al enviar email de restablecimiento: {error_msg}")
            return Response(
                {'error': 'Correo electrónico inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Excepción al restablecer contraseña: {e}")
            import traceback
            traceback.print_exc()
        # Por seguridad, devolver mensaje genérico
        return Response(
            {'error': 'Correo electrónico inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    Cierra la sesión del usuario actual.
    """
    try:
        django_logout(request)
        return Response({'success': True, 'message': 'Sesión cerrada correctamente'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([])  # Sin autenticación requerida para reset password confirm
def reset_password_confirm(request):
    """API para verificar código y cambiar contraseña usando Firebase"""
    oob_code = request.data.get('oobCode')
    new_password = request.data.get('newPassword')
    
    if not oob_code or not new_password:
        return Response(
            {'error': 'Código y nueva contraseña son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validar longitud mínima de contraseña
    if len(new_password) < 6:
        return Response(
            {'error': 'La contraseña debe tener al menos 6 caracteres'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from ..firebase_service import verify_password_reset_code_and_change_password
        result = verify_password_reset_code_and_change_password(oob_code, new_password)
        
        if result.get('success'):
            return Response({
                'message': result.get('message', 'Contraseña cambiada exitosamente'),
                'success': True
            })
        else:
            error_msg = result.get('error', 'Error al cambiar la contraseña')
            # Mapear errores comunes de Firebase a mensajes más amigables
            if 'INVALID_OOB_CODE' in error_msg or 'expired' in error_msg.lower():
                error_msg = 'El código de verificación es inválido o ha expirado'
            elif 'WEAK_PASSWORD' in error_msg:
                error_msg = 'La contraseña es muy débil. Usa una contraseña más segura'
            
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        if settings.DEBUG:
            print(f"ERROR: Excepción al confirmar restablecimiento de contraseña: {e}")
            import traceback
            traceback.print_exc()
        return Response(
            {'error': 'Error al procesar la solicitud. Por favor, intenta más tarde.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([])  # Sin autenticación requerida para login
def api_login(request):
    """API de login que devuelve JSON"""
    from django.contrib.auth import authenticate, login
    from django.conf import settings
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Usuario y contraseña son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        if settings.DEBUG:
            print(f"DEBUG api_login: Intentando autenticar usuario: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if settings.DEBUG:
            print(f"DEBUG api_login: Resultado authenticate: {user}")
            if user:
                print(f"DEBUG api_login: Usuario encontrado: {user.username}, Activo: {user.is_active}")
        
        if user is not None:
            if user.is_active:
                login(request, user)
                serializer = UserSerializer(user)
                if settings.DEBUG:
                    print(f"DEBUG api_login: Login exitoso, devolviendo datos del usuario")
                return Response(serializer.data)
            else:
                if settings.DEBUG:
                    print(f"DEBUG api_login: Usuario inactivo")
                return Response(
                    {'error': 'Usuario inactivo'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            if settings.DEBUG:
                print(f"DEBUG api_login: Usuario o contraseña incorrectos")
            return Response(
                {'error': 'Usuario o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        if settings.DEBUG:
            import traceback
            print(f"ERROR api_login: Excepción: {e}")
            traceback.print_exc()
        return Response(
            {'error': f'Error al iniciar sesión: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

