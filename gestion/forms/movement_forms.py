# gestion/forms/movement_forms.py

import re
from django import forms
from django.core.validators import MinValueValidator
from ..models import Product, Zone, Warehouse, Supplier, ProductMovement

class ProductMovementForm(forms.ModelForm):
    """
    Formulario de Movimiento de Productos según especificación
    Con tabs: Datos del movimiento, Control avanzado, Referencias/Observaciones
    """
    
    class Meta:
        model = ProductMovement
        fields = [
            # Datos del movimiento
            'fecha', 'tipo', 'cantidad', 'product', 'supplier', 'warehouse',
            'origin_zone', 'destination_zone',
            # Control avanzado
            'lote', 'serie', 'fecha_vencimiento',
            # Referencias/Observaciones
            'doc_referencia', 'motivo', 'observaciones'
        ]
        
        widgets = {
            'fecha': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}, choices=ProductMovement.MOVEMENT_TYPES),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'min': '0.0001'}),
            'product': forms.Select(attrs={'class': 'form-select'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'origin_zone': forms.Select(attrs={'class': 'form-select'}),
            'destination_zone': forms.Select(attrs={'class': 'form-select'}),
            'lote': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'serie': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'doc_referencia': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': '1000'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        self.fields['supplier'].queryset = Supplier.objects.filter(estado='ACTIVO')
        self.fields['warehouse'].queryset = Warehouse.objects.filter(is_active=True)
        self.fields['origin_zone'].queryset = Zone.objects.filter(is_active=True)
        self.fields['destination_zone'].queryset = Zone.objects.filter(is_active=True)
        
        # Campos requeridos base
        self.fields['fecha'].required = True
        self.fields['tipo'].required = True
        self.fields['cantidad'].required = True
        self.fields['product'].required = True
        
        # Determinar tipo de movimiento
        # Primero intentar desde los datos del formulario (request.data en DRF)
        tipo = None
        # self.data puede ser QueryDict o dict en DRF
        if hasattr(self, 'data') and self.data:
            if isinstance(self.data, dict):
                tipo = self.data.get('tipo')
            elif hasattr(self.data, 'get'):
                tipo = self.data.get('tipo')
        if not tipo and self.initial and 'tipo' in self.initial:
            tipo = self.initial.get('tipo')
        if not tipo and self.instance and self.instance.pk:
            tipo = self.instance.tipo
        if not tipo:
            tipo = 'ingreso'  # Default
        
        # Configurar campos requeridos según tipo de movimiento
        if tipo == 'ingreso':
            self.fields['supplier'].required = False
            self.fields['warehouse'].required = True
            self.fields['origin_zone'].required = False
            self.fields['destination_zone'].required = True
        elif tipo == 'salida':
            self.fields['supplier'].required = False
            self.fields['warehouse'].required = True
            self.fields['origin_zone'].required = True
            self.fields['destination_zone'].required = False
        elif tipo == 'transferencia':
            self.fields['supplier'].required = False
            self.fields['warehouse'].required = False  # No requerido para transferencias
            self.fields['origin_zone'].required = True
            self.fields['destination_zone'].required = True
        elif tipo == 'ajuste':
            self.fields['supplier'].required = False
            self.fields['warehouse'].required = False
            self.fields['origin_zone'].required = False
            self.fields['destination_zone'].required = True
        elif tipo == 'devolucion':
            self.fields['supplier'].required = False
            self.fields['warehouse'].required = False
            self.fields['origin_zone'].required = False
            self.fields['destination_zone'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        cantidad = cleaned_data.get('cantidad')
        origin_zone = cleaned_data.get('origin_zone')
        destination_zone = cleaned_data.get('destination_zone')
        product = cleaned_data.get('product')
        
        # Validaciones según tipo de movimiento
        if tipo == 'transferencia':
            if not origin_zone or not destination_zone:
                raise forms.ValidationError({
                    'origin_zone': 'Las transferencias requieren zona de origen y destino.',
                    'destination_zone': 'Las transferencias requieren zona de origen y destino.'
                })
            if origin_zone == destination_zone:
                raise forms.ValidationError({
                    'destination_zone': 'La zona de destino debe ser diferente a la de origen.'
                })
        
        # Validar cantidad positiva
        if cantidad and cantidad <= 0:
            raise forms.ValidationError({
                'cantidad': 'La cantidad debe ser mayor que cero.'
            })
        
        # Validar lote
        lote = cleaned_data.get('lote')
        if lote and len(lote) > 100:
            raise forms.ValidationError({
                'lote': 'El número de lote no puede tener más de 100 caracteres.'
            })
        
        # Validar serie
        serie = cleaned_data.get('serie')
        if serie and len(serie) > 100:
            raise forms.ValidationError({
                'serie': 'El número de serie no puede tener más de 100 caracteres.'
            })
        
        # Validar doc_referencia
        doc_referencia = cleaned_data.get('doc_referencia')
        if doc_referencia and len(doc_referencia) > 100:
            raise forms.ValidationError({
                'doc_referencia': 'El documento de referencia no puede tener más de 100 caracteres.'
            })
        
        # Validar motivo
        motivo = cleaned_data.get('motivo')
        if motivo and len(motivo) > 1000:
            raise forms.ValidationError({
                'motivo': 'El motivo no puede tener más de 1000 caracteres.'
            })
        
        # Validar observaciones
        observaciones = cleaned_data.get('observaciones')
        if observaciones and len(observaciones) > 1000:
            raise forms.ValidationError({
                'observaciones': 'Las observaciones no pueden tener más de 1000 caracteres.'
            })
        
        return cleaned_data
