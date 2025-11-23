# gestion/forms/product_supplier_forms.py

from django import forms
from ..models import ProductSupplier, Product, Supplier

class ProductSupplierForm(forms.ModelForm):
    """
    Formulario para la relación Producto-Proveedor
    """
    
    class Meta:
        model = ProductSupplier
        fields = ['product', 'supplier', 'costo', 'lead_time_dias', 'min_lote', 
                  'descuento_pct', 'preferente']
        
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'lead_time_dias': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'min_lote': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'descuento_pct': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'max': '100'}),
            'preferente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)
        if product:
            self.fields['product'].queryset = Product.objects.filter(pk=product.pk)
            self.fields['product'].initial = product
            self.fields['product'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('product')
        proveedor = cleaned_data.get('supplier')
        preferente = cleaned_data.get('preferente', False)
        
        # Si se marca como preferente, desmarcar otros proveedores preferentes del mismo producto
        if preferente and producto and proveedor:
            ProductSupplier.objects.filter(
                product=producto,
                preferente=True
            ).exclude(
                supplier=proveedor
            ).update(preferente=False)
        
        return cleaned_data

