# gestion/views/api_views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db import transaction
from django.views.decorators.http import require_http_methods
from decimal import Decimal
import json
from ..models import Inventory, Zone, Product, Sale, SaleItem, Client, SupplierOrder, SupplierOrderItem

@login_required
def get_product_stock_info(request, product_id):
    """
    Devuelve las zonas (y su stock) que tienen un producto específico.
    """
    try:
        # Buscamos en el inventario solo las entradas para este producto
        # que SÍ tienen stock (quantity > 0)
        stock_items = Inventory.objects.filter(
            product_id=product_id, 
            quantity__gt=0
        ).select_related('zone', 'zone__warehouse') # Optimizamos la consulta

        zones_with_stock = []
        for item in stock_items:
            zones_with_stock.append({
                'zone_id': item.zone.id,
                'zone_name': str(item.zone), # Ej: "Zona A (en Bodega Central)"
                'stock': item.quantity
            })
        
        return JsonResponse({'status': 'success', 'stock_info': zones_with_stock})
    
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

@login_required
def get_all_zones(request):
    """
    Devuelve TODAS las zonas (para el dropdown de destino).
    """
    zones = Zone.objects.filter(is_active=True).select_related('warehouse')
    all_zones_list = [
        {'id': zone.id, 'name': str(zone)}
        for zone in zones
    ]
    return JsonResponse({'status': 'success', 'zones': all_zones_list})


@login_required
def get_zones_by_warehouse(request, warehouse_id):
    """
    Devuelve las zonas de una bodega específica.
    """
    try:
        zones = Zone.objects.filter(warehouse_id=warehouse_id, is_active=True).select_related('warehouse')
        zones_list = [
            {'id': zone.id, 'name': str(zone)}
            for zone in zones
        ]
        return JsonResponse({'status': 'success', 'zones': zones_list})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# --- HELPER FUNCTION: Obtener zona de ventas ---
def get_sales_zone():
    """
    Busca la zona de ventas. Intenta por nombre "Ventas" o similar.
    Si no existe, toma la primera zona activa.
    """
    try:
        # Primero intentamos buscar una zona con nombre que contenga "venta"
        sales_zone = Zone.objects.filter(
            name__icontains='venta',
            is_active=True
        ).first()
        
        if not sales_zone:
            # Si no existe, tomamos la primera zona activa
            sales_zone = Zone.objects.filter(is_active=True).first()
        
        return sales_zone
    except:
        return None

# --- API: Buscar productos para venta ---
@login_required
def search_products_for_sale(request):
    """
    Busca productos por nombre o SKU y devuelve su precio y 
    el stock DISPONIBLE en la ZONA DE VENTAS.
    """
    query = request.GET.get('q', '')
    if len(query) < 2: # No buscar con menos de 2 caracteres
        return JsonResponse({'status': 'error', 'message': 'Query muy corto'}, status=400)

    try:
        # 1. Buscamos productos que coincidan
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(sku__icontains=query),
            is_active=True
        )[:10] # Limitamos a 10 resultados

        # 2. Obtenemos la zona de ventas
        sales_zone = get_sales_zone()
        if not sales_zone:
            return JsonResponse({'status': 'error', 'message': 'Zona de ventas no configurada'}, status=500)

        results = []
        for product in products:
            # 3. Buscamos el stock Específico de ese producto EN esa zona
            try:
                stock_item = Inventory.objects.get(product=product, zone=sales_zone)
                available_stock = stock_item.quantity
            except Inventory.DoesNotExist:
                available_stock = 0 # No hay stock en la zona de ventas

            results.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'price': str(product.price),  # Convertir a string para JSON
                'stock': available_stock # Stock solo de la zona de ventas
            })
        
        return JsonResponse({'status': 'success', 'products': results})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# --- API: Procesar venta ---
@login_required
@require_http_methods(["POST"])
def process_sale(request):
    """
    Procesa una venta: crea la venta, los items, y descuenta stock.
    """
    try:
        data = json.loads(request.body)
        client_id = data.get('client_id')
        cart = data.get('cart', [])  # Lista de {id: producto_id, quantity: cantidad}
        
        if not cart:
            return JsonResponse({'status': 'error', 'errors': 'El carrito está vacío'}, status=400)
        
        sales_zone = get_sales_zone()
        if not sales_zone:
            return JsonResponse({'status': 'error', 'errors': 'Zona de ventas no configurada'}, status=500)
        
        # Validar stock antes de procesar
        errors = []
        for item in cart:
            product_id = item.get('id')
            quantity = item.get('quantity', 0)
            
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
                    errors.append(f"No hay stock de {product.name} en la zona de ventas")
            except Product.DoesNotExist:
                errors.append(f"Producto con ID {product_id} no encontrado")
        
        if errors:
            return JsonResponse({'status': 'error', 'errors': '<br>'.join(errors)}, status=400)
        
        # Si todo está bien, procesamos la venta
        with transaction.atomic():
            # 1. Crear la venta
            sale = Sale.objects.create(
                client_id=client_id if client_id else None,
                user=request.user,
                total_amount=Decimal('0.00')  # Se calculará al final
            )
            
            total_amount = Decimal('0.00')
            
            # 2. Crear los items y descontar stock
            for item in cart:
                product_id = item.get('id')
                quantity = item.get('quantity', 0)
                
                product = Product.objects.get(id=product_id)
                inventory = Inventory.objects.get(product=product, zone=sales_zone)
                
                # Crear el item de venta
                item_price = product.price * Decimal(quantity)
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price_at_sale=product.price
                )
                
                # Descontar stock
                inventory.quantity -= quantity
                inventory.save()
                
                total_amount += item_price
            
            # 3. Actualizar el total de la venta
            sale.total_amount = total_amount
            sale.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Venta #{sale.id} procesada exitosamente. Total: ${total_amount:,.0f}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'errors': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'errors': f'Error del servidor: {str(e)}'}, status=500)


@login_required
def get_product_price(request, product_id):
    """
    Devuelve el precio de un producto específico.
    """
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        return JsonResponse({
            'status': 'success',
            'price': str(product.price),
            'name': product.name
        })
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def add_product_to_order(request, order_pk):
    """
    API para agregar un producto a una orden usando AJAX.
    """
    if not (request.user.is_superuser or hasattr(request.user, 'profile') and 
            (request.user.profile.role == 'admin' or request.user.profile.role == 'bodega')):
        return JsonResponse({'status': 'error', 'message': 'No tienes permisos'}, status=403)
    
    try:
        order = SupplierOrder.objects.get(pk=order_pk)
        
        if order.status != 'PENDING':
            return JsonResponse({'status': 'error', 'message': 'No se pueden modificar órdenes que no están pendientes'}, status=400)
        
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser mayor a 0'}, status=400)
        
        product = Product.objects.get(pk=product_id, is_active=True)
        
        # Verificar que el producto pertenece al proveedor de la orden
        if product.supplier != order.supplier:
            return JsonResponse({'status': 'error', 'message': 'Este producto no pertenece al proveedor de la orden'}, status=400)
        
        # Verificar si el producto ya está en la orden
        existing_item = SupplierOrderItem.objects.filter(order=order, product=product).first()
        
        if existing_item:
            # Si ya existe, actualizar la cantidad
            existing_item.quantity += quantity
            existing_item.save()
            item = existing_item
            action = 'updated'
        else:
            # Si no existe, crear nuevo item
            item = SupplierOrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price
            )
            action = 'created'
        
        # Obtener todos los items actualizados
        items = SupplierOrderItem.objects.filter(order=order).select_related('product')
        items_data = []
        total_quantity = 0
        for order_item in items:
            items_data.append({
                'id': order_item.id,
                'product_name': order_item.product.name,
                'quantity': order_item.quantity,
                'unit_price': str(order_item.unit_price),
                'subtotal': str(order_item.subtotal)
            })
            total_quantity += order_item.quantity
        
        return JsonResponse({
            'status': 'success',
            'message': f'Producto {product.name} agregado exitosamente',
            'action': action,
            'item': {
                'id': item.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal)
            },
            'all_items': items_data,
            'total_items': len(items_data),
            'total_quantity': total_quantity
        })
        
    except SupplierOrder.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Orden no encontrada'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def get_order_items(request, order_pk):
    """
    API para obtener los items de una orden en formato JSON.
    """
    try:
        order = SupplierOrder.objects.get(pk=order_pk)
        items = SupplierOrderItem.objects.filter(order=order).select_related('product')
        
        items_data = []
        total_quantity = 0
        for item in items:
            items_data.append({
                'id': item.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal)
            })
            total_quantity += item.quantity
        
        return JsonResponse({
            'status': 'success',
            'items': items_data,
            'total_items': len(items_data),
            'total_quantity': total_quantity
        })
    except SupplierOrder.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Orden no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
