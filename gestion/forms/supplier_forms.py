# gestion/forms/supplier_forms.py

import re
from django import forms
from django.core.validators import RegexValidator
from ..models import Supplier

# Validador de teléfono chileno/internacional
phone_validator = RegexValidator(
    regex=r'^(\+?56\s?)?[2-9]\d{8}$|^(\+?\d{1,3}\s?)?\d{8,15}$',
    message='Formato de teléfono inválido. Use formato: +56 9 1234 5678 o 912345678'
)

class SupplierForm(forms.ModelForm):
    telefono = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678',
            'maxlength': '30'
        }),
        help_text='Formato chileno: +56912345678 o 912345678'
    )
    
    contacto_principal_telefono = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56912345678',
            'maxlength': '30'
        }),
        help_text='Formato chileno: +56912345678 o 912345678'
    )
    
    class Meta:
        model = Supplier
        fields = [
            # Identificación legal y contacto
            'rut_nif', 'razon_social', 'nombre_fantasia',
            'email', 'telefono', 'sitio_web',
            # Dirección
            'direccion', 'ciudad', 'pais',
            # Comercial
            'condiciones_pago', 'moneda',
            'contacto_principal_nombre', 'contacto_principal_email', 'contacto_principal_telefono',
            'estado', 'observaciones'
        ]
        
        widgets = {
            'rut_nif': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '20',
                'placeholder': '76.123.456-7'
            }),
            'razon_social': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'Razón Social del Proveedor'
            }),
            'nombre_fantasia': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'Nombre de Fantasía (opcional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '254',
                'placeholder': 'email@proveedor.cl'
            }),
            'sitio_web': forms.URLInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'https://www.proveedor.cl'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'placeholder': 'Dirección completa'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '128',
                'placeholder': 'Ciudad'
            }),
            'pais': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '64',
                'placeholder': 'País'
            }),
            'condiciones_pago': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '100',
                'placeholder': 'Ej: 30 días, contado'
            }),
            'moneda': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('CLP', 'CLP - Peso Chileno'),
                ('USD', 'USD - Dólar'),
                ('EUR', 'EUR - Euro'),
                ('BRL', 'BRL - Real Brasileño'),
            ]),
            'contacto_principal_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '120',
                'placeholder': 'Nombre del contacto'
            }),
            'contacto_principal_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'maxlength': '254',
                'placeholder': 'email@contacto.cl'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'maxlength': '1000',
                'placeholder': 'Observaciones adicionales'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rut_nif'].required = True
        self.fields['razon_social'].required = True
        self.fields['email'].required = True
        self.fields['condiciones_pago'].required = True
        self.fields['moneda'].required = True
        self.fields['pais'].required = True
        
        # Agregar maxlength a todos los campos de texto
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.URLInput)):
                if 'maxlength' not in field.widget.attrs:
                    # Obtener maxlength del modelo
                    model_field = self.Meta.model._meta.get_field(field_name)
                    if hasattr(model_field, 'max_length'):
                        field.widget.attrs['maxlength'] = model_field.max_length
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar espacios y caracteres especiales para validación
            cleaned_phone = re.sub(r'[\s\-\(\)\.]', '', telefono)
            
            # Validar formato chileno: +56912345678, 56912345678, o 912345678
            # Debe empezar con +56, 56, o 9, seguido de 8 dígitos más (total 9 dígitos después del código de país)
            if not re.match(r'^(\+?56)?9\d{8}$', cleaned_phone):
                raise forms.ValidationError(
                    'El teléfono debe ser formato chileno (ej: +56912345678 o 912345678)'
                )
        return telefono
    
    def clean_contacto_principal_telefono(self):
        telefono = self.cleaned_data.get('contacto_principal_telefono')
        if telefono:
            # Limpiar espacios y caracteres especiales para validación
            cleaned_phone = re.sub(r'[\s\-\(\)\.]', '', telefono)
            
            # Validar formato chileno: +56912345678, 56912345678, o 912345678
            if not re.match(r'^(\+?56)?9\d{8}$', cleaned_phone):
                raise forms.ValidationError(
                    'El teléfono debe ser formato chileno (ej: +56912345678 o 912345678)'
                )
        return telefono
    
    def clean_rut_nif(self):
        rut_nif = self.cleaned_data.get('rut_nif')
        if rut_nif:
            # Verificar unicidad excluyendo la instancia actual si estamos editando
            queryset = Supplier.objects.filter(rut_nif__iexact=rut_nif)
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise forms.ValidationError("Este RUT/NIF ya está registrado. Debe ser único.")
        return rut_nif
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if len(email) > 254:
                raise forms.ValidationError("El email no puede tener más de 254 caracteres")
            # Validación de formato de email (Django ya lo hace, pero podemos mejorar el mensaje)
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except forms.ValidationError:
                raise forms.ValidationError("El email no tiene un formato válido")
        return email
    
    def clean_razon_social(self):
        razon_social = self.cleaned_data.get('razon_social')
        if razon_social:
            if len(razon_social) > 255:
                raise forms.ValidationError("La razón social no puede tener más de 255 caracteres")
        return razon_social
    
    def clean_nombre_fantasia(self):
        nombre_fantasia = self.cleaned_data.get('nombre_fantasia')
        if nombre_fantasia:
            if len(nombre_fantasia) > 255:
                raise forms.ValidationError("El nombre fantasía no puede tener más de 255 caracteres")
        return nombre_fantasia
    
    def clean_condiciones_pago(self):
        condiciones_pago = self.cleaned_data.get('condiciones_pago')
        if condiciones_pago:
            if len(condiciones_pago) > 100:
                raise forms.ValidationError("Las condiciones de pago no pueden tener más de 100 caracteres")
        return condiciones_pago
    
    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion')
        if direccion:
            if len(direccion) > 255:
                raise forms.ValidationError("La dirección no puede tener más de 255 caracteres")
        return direccion
    
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')
        if ciudad:
            if len(ciudad) > 128:
                raise forms.ValidationError("La ciudad no puede tener más de 128 caracteres")
        return ciudad
    
    def clean_pais(self):
        pais = self.cleaned_data.get('pais')
        if not pais:
            raise forms.ValidationError("El país es requerido")
        if len(pais) > 64:
            raise forms.ValidationError("El país no puede tener más de 64 caracteres")
        return pais
    
    def clean_contacto_principal_nombre(self):
        nombre = self.cleaned_data.get('contacto_principal_nombre')
        if nombre:
            if len(nombre) > 120:
                raise forms.ValidationError("El nombre del contacto no puede tener más de 120 caracteres")
        return nombre
    
    def clean_contacto_principal_email(self):
        email = self.cleaned_data.get('contacto_principal_email')
        if email:
            if len(email) > 254:
                raise forms.ValidationError("El email del contacto no puede tener más de 254 caracteres")
        return email
    
    def clean_observaciones(self):
        observaciones = self.cleaned_data.get('observaciones')
        if observaciones:
            if len(observaciones) > 1000:
                raise forms.ValidationError("Las observaciones no pueden tener más de 1000 caracteres")
        return observaciones
