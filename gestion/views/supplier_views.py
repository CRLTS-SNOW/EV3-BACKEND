from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin 
from django.urls import reverse_lazy
from django.db.models import Q

# ¡NUEVAS IMPORTACIONES PARA LA VISTA AJAX!
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
import io
import openpyxl
# ¡FIN DE NUEVAS IMPORTACIONES!

from ..models import Supplier, SupplierOrder
from ..forms.supplier_forms import SupplierForm
from ..auth_utils import is_admin, is_bodega_or_admin 

# --- APLICAMOS SEGURIDAD DE ROL 'ADMIN' ---

class SupplierListView(UserPassesTestMixin, ListView):
    model = Supplier
    template_name = 'gestion/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def test_func(self):
        return is_admin(self.request.user) or is_bodega_or_admin(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', None)
        
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(email__icontains=search_query)
            )
        
        # Ordenamiento
        sort_by = self.request.GET.get('sort', 'name')
        sort_options = {
            'name': 'name',  # Alfabético A-Z
            '-name': '-name',  # Alfabético Z-A
            'email': 'email',  # Email A-Z
            '-email': '-email',  # Email Z-A
        }
        
        if sort_by in sort_options:
            queryset = queryset.order_by(sort_options[sort_by])
        else:
            queryset = queryset.order_by('name')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        
        # Guardar búsqueda en sesión
        if 'q' in self.request.GET:
            self.request.session['supplier_search_query'] = self.request.GET.get('q', '')
        elif 'supplier_search_query' in self.request.session:
            context['search_query'] = self.request.session['supplier_search_query']
        
        # ... (El resto de tu lógica de get_context_data para órdenes)
        orders_queryset = SupplierOrder.objects.select_related('supplier', 'warehouse', 'zone', 'requested_by')
        order_status = self.request.GET.get('order_status', '')
        if order_status:
            orders_queryset = orders_queryset.filter(status=order_status)
        order_search = self.request.GET.get('order_q', '')
        if order_search:
            if order_search.isdigit():
                orders_queryset = orders_queryset.filter(id=order_search)
            else:
                orders_queryset = orders_queryset.filter(supplier__name__icontains=order_search)
        context['orders'] = orders_queryset.order_by('-order_date')[:20]
        context['order_status'] = order_status
        context['order_search'] = order_search
        
        # Guardar filtros de órdenes en sesión
        if 'order_status' in self.request.GET:
            self.request.session['order_status_filter'] = order_status
        elif 'order_status_filter' in self.request.session:
            context['order_status'] = self.request.session['order_status_filter']
        
        if 'order_q' in self.request.GET:
            self.request.session['order_search_query'] = order_search
        elif 'order_search_query' in self.request.session:
            context['order_search'] = self.request.session['order_search_query']
        
        return context


class SupplierCreateView(UserPassesTestMixin, CreateView):
    # ... (Tu vista CreateView sin cambios)
    model = Supplier
    form_class = SupplierForm
    template_name = 'gestion/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Proveedor'
        return context


class SupplierUpdateView(UserPassesTestMixin, UpdateView):
    # ... (Tu vista UpdateView sin cambios)
    model = Supplier
    form_class = SupplierForm
    template_name = 'gestion/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def test_func(self):
        return is_admin(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Proveedor'
        return context


# ----------------------------------------------------
# ¡NUEVA VISTA AJAX PARA LIVE SEARCH DE PROVEEDORES!
# ----------------------------------------------------
@login_required
def search_suppliers_live(request):
    """
    Busca proveedores por 'q' y devuelve el HTML de la tabla.
    """
    search_query = request.GET.get('q', '')
    
    # Replicamos la lógica de filtrado de SupplierListView
    queryset = Supplier.objects.all()
    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    queryset = queryset.order_by('name')
    
    context = {
        'suppliers': queryset,
    }

    # Renderizamos solo el cuerpo de la tabla
    html_results = render_to_string(
        'gestion/includes/supplier_table_body.html', 
        context, 
        request=request
    )
    return JsonResponse({'html': html_results})

# -----------------------------------------------------------
# ¡NUEVA VISTA AJAX PARA LIVE SEARCH DE ÓRDENES A PROVEEDOR!
# -----------------------------------------------------------
@login_required
def search_supplier_orders_live(request):
    """
    Busca órdenes por 'q' (ID o proveedor) y 'status', 
    y devuelve el HTML de la tabla.
    """
    search_query = request.GET.get('q', '')
    order_status = request.GET.get('status', '')
    
    # Replicamos la lógica de filtrado de SupplierListView.get_context_data
    orders_queryset = SupplierOrder.objects.select_related('supplier', 'warehouse', 'zone', 'requested_by')
    
    if order_status:
        orders_queryset = orders_queryset.filter(status=order_status)
    
    if search_query:
        if search_query.isdigit():
            orders_queryset = orders_queryset.filter(id=search_query)
        else:
            orders_queryset = orders_queryset.filter(supplier__name__icontains=search_query)
    
    context = {
        'orders': orders_queryset.order_by('-order_date')[:20], # Mostramos solo los 20 más recientes
    }

    # Renderizamos solo el cuerpo de la tabla
    html_results = render_to_string(
        'gestion/includes/supplier_order_table_body.html', 
        context, 
        request=request
    )
    return JsonResponse({'html': html_results})


# ----------------------------------------------------
# EXPORTAR PROVEEDORES A EXCEL
# ----------------------------------------------------
@login_required
def export_suppliers_excel(request):
    """
    Crea un archivo Excel con la lista de proveedores.
    """
    if not (is_admin(request.user) or is_bodega_or_admin(request.user)):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("No tienes permisos para exportar proveedores")
    
    suppliers = Supplier.objects.all().order_by('name')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lista de Proveedores"

    ws.append(['Nombre', 'Email', 'Teléfono', 'Estado', 'Fecha de Creación'])

    for supplier in suppliers:
        ws.append([
            supplier.name,
            supplier.email,
            supplier.phone or 'N/A',
            'Activo' if supplier.is_active else 'Inactivo',
            supplier.created_at.strftime('%d/%m/%Y %H:%M') if supplier.created_at else 'N/A'
        ])

    virtual_workbook = io.BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)

    response = HttpResponse(
        virtual_workbook.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="lista_proveedores.xlsx"'
    
    return response