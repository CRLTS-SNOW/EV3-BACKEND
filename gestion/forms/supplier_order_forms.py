# gestion/forms/supplier_order_forms.py

from django import forms
from ..models import Supplier, Warehouse, Zone, Product, SupplierOrder, SupplierOrderItem

class SupplierOrderForm(forms.ModelForm):
    """
    Formulario para crear una orden a proveedor.
    """
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.filter(is_active=True),
        label="Bodega Destino",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_warehouse'})
    )
    zone = forms.ModelChoiceField(
        queryset=Zone.objects.none(),
        label="Zona Destino",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_zone'})
    )
    
    class Meta:
        model = SupplierOrder
        fields = ['supplier', 'warehouse', 'zone', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        if 'warehouse' in self.data:
            try:
                warehouse_id = int(self.data.get('warehouse'))
                self.fields['zone'].queryset = Zone.objects.filter(warehouse_id=warehouse_id, is_active=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            if self.instance.warehouse:
                self.fields['zone'].queryset = Zone.objects.filter(
                    warehouse=self.instance.warehouse, 
                    is_active=True
                )


class SupplierOrderItemForm(forms.ModelForm):
    """
    Formulario para agregar items a una orden.
    El precio se toma automáticamente del producto.
    """
    product_price = forms.DecimalField(
        label="Precio Unitario",
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'id': 'id_product_price'
        }),
        help_text="El precio se toma automáticamente del producto"
    )
    
    class Meta:
        model = SupplierOrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select', 'id': 'id_product'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True).order_by('name')
        # No incluimos unit_price en el formulario, se asignará automáticamente
    
    def clean(self):
        cleaned_data = super().clean()
        # Validar que el producto tenga precio
        product = cleaned_data.get('product')
        if product and product.price <= 0:
            raise forms.ValidationError(f"El producto {product.name} no tiene un precio válido configurado.")
        return cleaned_data
    
    def save(self, commit=True):
        item = super().save(commit=False)
        # El precio se toma automáticamente del producto
        if item.product:
            item.unit_price = item.product.price
        if commit:
            item.save()
        return item

