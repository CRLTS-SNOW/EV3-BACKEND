# gestion/views/product_views.py

import io
from django.http import HttpResponse, JsonResponse
import openpyxl
from django.views.generic import ListView
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.shortcuts import render # Agregado por si es necesario
from django.template.loader import render_to_string # ¡Nueva Importación para AJAX!
from ..models import Product, UserProfile
from ..forms.movement_forms import ProductMovementForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'gestion/product_list.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_paginate_by(self, queryset):
        """
        Permite que el usuario elija cuántos productos mostrar por página.
        """
        per_page = self.request.GET.get('per_page', '20')
        # Validar que sea uno de los valores permitidos
        allowed_values = ['10', '20', '30']
        if per_page in allowed_values:
            return int(per_page)
        return 20  # Valor por defecto (cambié de 15 a 20)

    def get_queryset(self):
        # Todos pueden ver el queryset base
        queryset = super().get_queryset().filter(is_active=True).select_related('supplier')
        
        # Anotar el stock total y filtrar productos con stock > 0
        queryset = queryset.annotate(
            total_stock=Coalesce(Sum('stock__quantity'), 0)
        ).filter(total_stock__gt=0)
        
        search_query = self.request.GET.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(sku__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )

        sort_by = self.request.GET.get('sort', 'name')
        # Opciones de ordenamiento: nombre (alfabético), stock, precio
        sort_options = {
            'name': 'name',  # Alfabético A-Z
            '-name': '-name',  # Alfabético Z-A
            'stock': 'total_stock',  # Stock menor a mayor
            '-stock': '-total_stock',  # Stock mayor a menor
            'price': 'price',  # Precio menor a mayor
            '-price': '-price',  # Precio mayor a menor
            'sku': 'sku',  # SKU A-Z
            '-sku': '-sku',  # SKU Z-A
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('name')  # Por defecto alfabético

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        context['per_page'] = self.request.GET.get('per_page', '20')
        
        # Agregar el formulario de movimientos (solo si tiene permisos)
        if hasattr(self.request.user, 'profile'):
            role = self.request.user.profile.role
            if self.request.user.is_superuser or role == 'admin' or role == 'bodega':
                context['movement_form'] = ProductMovementForm()
            else:
                context['movement_form'] = None
        elif self.request.user.is_superuser:
            context['movement_form'] = ProductMovementForm()
        else:
            context['movement_form'] = None
        
        return context


@login_required
def export_products_excel(request):
    """
    Crea un archivo Excel en memoria y lo devuelve como una descarga.
    """
    products = Product.objects.all().select_related('supplier')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    ws.append(['Nombre', 'SKU', 'Proveedor', 'Precio', 'Stock Total'])

    for product in products:
        ws.append([
            product.name,
            product.sku,
            product.supplier.name if product.supplier else 'N/A',
            product.price,
            product.total_quantity
        ])

    # --- Corrección para guardar en memoria ---
    virtual_workbook = io.BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)

    response = HttpResponse(
        virtual_workbook.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
    
    return response


# ----------------------------------------------------
# VISTA AJAX PARA LA BÚSQUEDA EN VIVO (LIVE SEARCH)
# ----------------------------------------------------
@login_required
def search_products_live(request):
    """
    Busca productos por término (q) y devuelve el fragmento HTML de la tabla 
    (sin paginación) para actualizar la página vía AJAX.
    """
    
    # ¡HEMOS ELIMINADO LA COMPROBACIÓN DE 'x-requested-with' QUE DABA ERROR 400!

    # 1. Obtener parámetros de la URL
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'name')
    
    # 2. Base Queryset - Anotar stock total y filtrar productos con stock > 0
    queryset = Product.objects.filter(is_active=True).select_related('supplier')
    queryset = queryset.annotate(
        total_stock=Coalesce(Sum('stock__quantity'), 0)
    ).filter(total_stock__gt=0)

    # 3. Aplicar filtrado por búsqueda
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(supplier__name__icontains=search_query)
        )
    
    # 4. Aplicar ordenamiento
    sort_options = {
        'name': 'name',
        '-name': '-name',
        'stock': 'total_stock',
        '-stock': '-total_stock',
        'price': 'price',
        '-price': '-price',
        'sku': 'sku',
        '-sku': '-sku',
    }
    
    if sort_by in sort_options:
        queryset = queryset.order_by(sort_options[sort_by])
    else:
        queryset = queryset.order_by('name')
    
    # 5. Renderizar el fragmento de la tabla
    context = {
        'products': queryset,
        'search_query': search_query, 
        'current_sort': sort_by,
    }

    # Renderizamos solo el cuerpo de la tabla usando el template parcial
    html_results = render_to_string(
        'gestion/includes/product_table_body.html', 
        context, 
        request=request
    )

    # 6. Devolver la respuesta en formato JSON
    return JsonResponse({'html': html_results})