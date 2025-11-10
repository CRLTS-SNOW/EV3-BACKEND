# gestion/views/sale_views.py

from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
import io
import openpyxl
from django.http import HttpResponse

from ..models import Sale, Client, Product, Inventory, Zone
from ..auth_utils import is_ventas_or_admin

# --- VISTAS DE VENTAS ---

class SaleListView(UserPassesTestMixin, ListView):
    model = Sale
    template_name = 'gestion/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 20
    
    def test_func(self):
        return is_ventas_or_admin(self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'user').prefetch_related('items')
        
        # Buscar por cliente o ID de venta
        search_query = self.request.GET.get('q', None)
        if search_query:
            if search_query.isdigit():
                # Si es un número, buscar por ID exacto
                queryset = queryset.filter(id=search_query)
            else:
                # Si es texto, buscar por nombre de cliente
                queryset = queryset.filter(client__name__icontains=search_query)
        
        # Ordenamiento
        sort_by = self.request.GET.get('sort', '-sale_date')
        sort_options = {
            'date': '-sale_date',  # Fecha más reciente primero
            '-date': 'sale_date',  # Fecha más antigua primero
            'client': 'client__name',  # Cliente A-Z
            '-client': '-client__name',  # Cliente Z-A
            'total': 'total_amount',  # Total menor a mayor
            '-total': '-total_amount',  # Total mayor a menor
            'id': 'id',  # ID menor a mayor
            '-id': '-id',  # ID mayor a menor
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('-sale_date')  # Por defecto fecha más reciente
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-sale_date')
        
        # Guardar búsqueda en sesión
        if 'q' in self.request.GET:
            self.request.session['sale_search_query'] = self.request.GET.get('q', '')
        elif 'sale_search_query' in self.request.session:
            context['search_query'] = self.request.session['sale_search_query']
        
        return context


@login_required
def sale_create_view(request):
    """
    Vista para crear una nueva venta (POS).
    """
    if not is_ventas_or_admin(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("No tienes permisos para realizar ventas")
    
    clients = Client.objects.all().order_by('name')
    
    # Obtener la zona de ventas
    from .api_views import get_sales_zone
    sales_zone = get_sales_zone()
    
    # Obtener productos con stock en la zona de ventas
    products_with_stock = []
    if sales_zone:
        # Obtener inventarios con stock > 0 en la zona de ventas
        inventories = Inventory.objects.filter(
            zone=sales_zone,
            quantity__gt=0
        ).select_related('product').order_by('product__name')
        
        for inventory in inventories:
            if inventory.product.is_active:
                products_with_stock.append({
                    'id': inventory.product.id,
                    'name': inventory.product.name,
                    'sku': inventory.product.sku,
                    'price': str(inventory.product.price),
                    'stock': inventory.quantity
                })
    
    return render(request, 'gestion/sale_form.html', {
        'clients': clients,
        'products_with_stock': products_with_stock
    })


class SaleDetailView(UserPassesTestMixin, DetailView):
    model = Sale
    template_name = 'gestion/sale_detail.html'
    context_object_name = 'sale'
    
    def test_func(self):
        return is_ventas_or_admin(self.request.user)
    
    def get_queryset(self):
        return super().get_queryset().select_related('client', 'user').prefetch_related('items__product')


# ----------------------------------------------------
# VISTA AJAX PARA LIVE SEARCH DE VENTAS
# ----------------------------------------------------
@login_required
def search_sales_live(request):
    """
    Busca ventas por 'q' (cliente o ID) y devuelve el HTML de la tabla.
    """
    if not is_ventas_or_admin(request.user):
        return JsonResponse({'html': '<tr><td colspan="6" class="text-center text-danger">No tienes permisos.</td></tr>'})
    
    search_query = request.GET.get('q', '')
    
    queryset = Sale.objects.all().select_related('client', 'user').prefetch_related('items')
    if search_query:
        if search_query.isdigit():
            queryset = queryset.filter(id=search_query)
        else:
            queryset = queryset.filter(client__name__icontains=search_query)
    
    # Ordenamiento
    sort_by = request.GET.get('sort', '-sale_date')
    sort_options = {
        'date': '-sale_date',
        '-date': 'sale_date',
        'client': 'client__name',
        '-client': '-client__name',
        'total': 'total_amount',
        '-total': '-total_amount',
        'id': 'id',
        '-id': '-id',
    }
    
    if sort_by in sort_options:
        queryset = queryset.order_by(sort_options[sort_by])
    else:
        queryset = queryset.order_by('-sale_date')
    
    context = {
        'sales': queryset,
    }

    html_results = render_to_string(
        'gestion/includes/sale_table_body.html', 
        context, 
        request=request
    )
    return JsonResponse({'html': html_results})


# ----------------------------------------------------
# EXPORTAR VENTAS A EXCEL
# ----------------------------------------------------
@login_required
def export_sales_excel(request):
    """
    Crea un archivo Excel con el historial de ventas.
    """
    if not is_ventas_or_admin(request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("No tienes permisos para exportar ventas")
    
    sales = Sale.objects.all().select_related('client', 'user').prefetch_related('items__product')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Historial de Ventas"

    ws.append(['ID Venta', 'Fecha', 'Cliente', 'Vendedor', 'Total', 'Items'])

    for sale in sales:
        items_str = ', '.join([f"{item.quantity}x {item.product.name if item.product else 'N/A'}" for item in sale.items.all()])
        ws.append([
            sale.id,
            sale.sale_date.strftime('%d/%m/%Y %H:%M'),
            sale.client.name if sale.client else 'Cliente Varios',
            sale.user.username if sale.user else 'N/A',
            sale.total_amount,
            items_str
        ])

    virtual_workbook = io.BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)

    response = HttpResponse(
        virtual_workbook.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.xlsx"'
    
    return response

