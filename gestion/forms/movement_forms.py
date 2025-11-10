# gestion/forms/movement_forms.py

from django import forms
from ..models import Product, Zone, Inventory, ProductMovement

class ProductMovementForm(forms.ModelForm):
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    origin_zone = forms.ModelChoiceField(
        queryset=Zone.objects.filter(is_active=True),
        required=True, 
        label="Zona de Origen",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    destination_zone = forms.ModelChoiceField(
        queryset=Zone.objects.filter(is_active=True),
        required=True, 
        label="Zona de Destino",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    quantity = forms.IntegerField(
        min_value=1, 
        label="Cantidad a Mover",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    reason = forms.CharField(
        required=False,
        label="Motivo (Opcional)",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = ProductMovement
        fields = [
            'product', 
            'quantity', 
            'origin_zone', 
            'destination_zone',
            'reason'
        ]

    def clean(self):
        """
        Validación de stock disponible en la zona de origen.
        """
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        origin = cleaned_data.get('origin_zone')
        destination = cleaned_data.get('destination_zone')
        product = cleaned_data.get('product')

        if not (quantity and origin and destination and product):
            return cleaned_data 

        if origin == destination:
             raise forms.ValidationError(
                    "La Zona de Origen y Destino no pueden ser la misma."
                )

        try:
            inventory = Inventory.objects.get(product=product, zone=origin)
            if inventory.quantity < quantity:
                raise forms.ValidationError(
                    f"Stock insuficiente en {origin.name}. "
                    f"Solo hay {inventory.quantity} unidades."
                )
        except Inventory.DoesNotExist:
            raise forms.ValidationError(
                f"No existe stock de este producto en la zona {origin.name}."
            )

        return cleaned_data

