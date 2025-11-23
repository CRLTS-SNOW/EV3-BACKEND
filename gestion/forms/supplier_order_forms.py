# gestion/forms/supplier_order_forms.py

from django import forms
from django.core.validators import MinValueValidator
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
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(estado='ACTIVO')
        self.fields['supplier'].required = True
        self.fields['warehouse'].required = True
        self.fields['zone'].required = True
        
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
    
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if notes and len(notes) > 1000:
            raise forms.ValidationError("Las notas no pueden tener más de 1000 caracteres")
        return notes


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
        self.fields['product'].required = True
        self.fields['quantity'].required = True
        self.fields['quantity'].validators = [MinValueValidator(1)]
        # No incluimos unit_price en el formulario, se asignará automáticamente
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None:
            if quantity < 1:
                raise forms.ValidationError("La cantidad debe ser al menos 1")
            if quantity > 999999:
                raise forms.ValidationError("La cantidad es demasiado alta")
        return quantity
    
    def clean(self):
        cleaned_data = super().clean()
        # Validar que el producto tenga precio
        product = cleaned_data.get('product')
        if product and (not product.precio_venta or product.precio_venta <= 0):
            raise forms.ValidationError(f"El producto {product.name} no tiene un precio válido configurado.")
        return cleaned_data
    
    def save(self, commit=True):
        item = super().save(commit=False)
        # El precio se toma automáticamente del producto (precio_venta)
        if item.product:
            item.unit_price = item.product.precio_venta or 0
        if commit:
            item.save()
        return item

