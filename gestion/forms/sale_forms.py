# gestion/forms/sale_forms.py

import re
from django import forms
from django.core.validators import EmailValidator
from ..models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'rut', 'email', 'phone']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'rut': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12', 'placeholder': '12.345.678-9'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'maxlength': '150'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20', 'placeholder': '+56912345678'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("El nombre es requerido")
        if len(name) > 200:
            raise forms.ValidationError("El nombre no puede tener más de 200 caracteres")
        return name
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            if len(rut) > 12:
                raise forms.ValidationError("El RUT no puede tener más de 12 caracteres")
            # Validar formato básico de RUT chileno
            rut_clean = rut.replace('.', '').replace('-', '').upper()
            if not re.match(r'^\d{7,8}[0-9K]$', rut_clean):
                raise forms.ValidationError("El RUT no tiene un formato válido (ej: 12.345.678-9)")
        return rut
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if len(email) > 150:
                raise forms.ValidationError("El email no puede tener más de 150 caracteres")
            validator = EmailValidator()
            try:
                validator(email)
            except forms.ValidationError:
                raise forms.ValidationError("El email no tiene un formato válido")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if len(phone) > 20:
                raise forms.ValidationError("El teléfono no puede tener más de 20 caracteres")
            # Validar formato chileno
            phone_clean = re.sub(r'[\s\-\(\)\.]', '', phone)
            if not re.match(r'^(\+?56)?9\d{8}$', phone_clean):
                raise forms.ValidationError("El teléfono debe ser formato chileno (ej: +56912345678 o 912345678)")
        return phone

