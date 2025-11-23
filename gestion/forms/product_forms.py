# gestion/forms/product_forms.py

import re
from django import forms
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from ..models import Product

class ProductForm(forms.ModelForm):
    """
    Formulario de Producto según especificación
    Con tabs: Identificación y precios, Stock y control, Relaciones y derivados
    """
    
    class Meta:
        model = Product
        fields = [
            # Identificación
            'ean_upc', 'name', 'descripcion', 'categoria', 'marca', 'modelo',
            # Unidades y precios
            'uom_compra', 'uom_venta', 'factor_conversion', 'costo_estandar', 
            'precio_venta', 'impuesto_iva',
            # Stock y control
            'stock_minimo', 'stock_maximo', 'punto_reorden',
            'perishable', 'control_por_lote', 'control_por_serie',
            # Relaciones y soporte
            'imagen_url', 'ficha_tecnica_url',
            'is_active'
        ]
        
        widgets = {
            # Identificación
            'ean_upc': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '50'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '200'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'marca': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            # Unidades y precios
            'uom_compra': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('UN', 'Unidad (UN)'),
                ('CAJA', 'Caja (CAJA)'),
                ('KG', 'Kilogramo (KG)'),
                ('LT', 'Litro (LT)'),
                ('M', 'Metro (M)'),
            ]),
            'uom_venta': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('UN', 'Unidad (UN)'),
                ('CAJA', 'Caja (CAJA)'),
                ('KG', 'Kilogramo (KG)'),
                ('LT', 'Litro (LT)'),
                ('M', 'Metro (M)'),
            ]),
            'factor_conversion': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'costo_estandar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'impuesto_iva': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            # Stock y control
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'stock_maximo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'punto_reorden': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'perishable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_lote': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'control_por_serie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Relaciones y soporte
            'imagen_url': forms.URLInput(attrs={'class': 'form-control'}),
            'ficha_tecnica_url': forms.URLInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['categoria'].required = True
        self.fields['uom_compra'].required = True
        self.fields['uom_venta'].required = True
        self.fields['factor_conversion'].required = True
        self.fields['impuesto_iva'].required = True
        self.fields['stock_minimo'].required = True
        self.fields['perishable'].required = True
        self.fields['control_por_lote'].required = True
        self.fields['control_por_serie'].required = True
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            if len(name) > 200:
                raise forms.ValidationError("El nombre no puede tener más de 200 caracteres")
        return name
    
    def clean_categoria(self):
        categoria = self.cleaned_data.get('categoria')
        if categoria:
            if len(categoria) > 100:
                raise forms.ValidationError("La categoría no puede tener más de 100 caracteres")
        return categoria
    
    def clean_marca(self):
        marca = self.cleaned_data.get('marca')
        if marca:
            if len(marca) > 100:
                raise forms.ValidationError("La marca no puede tener más de 100 caracteres")
        return marca
    
    def clean_modelo(self):
        modelo = self.cleaned_data.get('modelo')
        if modelo:
            if len(modelo) > 100:
                raise forms.ValidationError("El modelo no puede tener más de 100 caracteres")
        return modelo
    
    def clean_ean_upc(self):
        ean_upc = self.cleaned_data.get('ean_upc')
        if ean_upc:
            if len(ean_upc) > 50:
                raise forms.ValidationError("El código EAN/UPC no puede tener más de 50 caracteres")
            # Validar formato alphanumeric, dashes, underscores
            if not re.match(r'^[A-Z0-9\-_]+$', ean_upc, re.IGNORECASE):
                raise forms.ValidationError("El código EAN/UPC solo puede contener letras, números, guiones y guiones bajos")
        return ean_upc
    
    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')
        if descripcion and len(descripcion) > 2000:
            raise forms.ValidationError("La descripción no puede tener más de 2000 caracteres")
        return descripcion
    
    def clean_precio_venta(self):
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta is not None:
            if precio_venta < 0:
                raise forms.ValidationError("El precio de venta no puede ser negativo")
            if precio_venta > 999999999999999.99:
                raise forms.ValidationError("El precio de venta es demasiado alto")
        return precio_venta
    
    def clean_costo_estandar(self):
        costo_estandar = self.cleaned_data.get('costo_estandar')
        if costo_estandar is not None:
            if costo_estandar < 0:
                raise forms.ValidationError("El costo estándar no puede ser negativo")
            if costo_estandar > 999999999999.999999:
                raise forms.ValidationError("El costo estándar es demasiado alto")
        return costo_estandar
    
    def clean_factor_conversion(self):
        factor_conversion = self.cleaned_data.get('factor_conversion')
        if factor_conversion:
            if factor_conversion < 0.0001:
                raise forms.ValidationError("El factor de conversión debe ser al menos 0.0001")
            if factor_conversion > 9999.9999:
                raise forms.ValidationError("El factor de conversión es demasiado alto")
        return factor_conversion
    
    def clean_impuesto_iva(self):
        impuesto_iva = self.cleaned_data.get('impuesto_iva')
        if impuesto_iva is not None:
            if impuesto_iva < 0:
                raise forms.ValidationError("El impuesto IVA no puede ser negativo")
            if impuesto_iva > 100:
                raise forms.ValidationError("El impuesto IVA no puede ser mayor a 100%")
        return impuesto_iva
    
    def clean_stock_minimo(self):
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_minimo is not None:
            if stock_minimo < 0:
                raise forms.ValidationError("El stock mínimo no puede ser negativo")
        return stock_minimo
    
    def clean_stock_maximo(self):
        stock_maximo = self.cleaned_data.get('stock_maximo')
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if stock_maximo is not None:
            if stock_maximo < 0:
                raise forms.ValidationError("El stock máximo no puede ser negativo")
            if stock_minimo is not None and stock_maximo < stock_minimo:
                raise forms.ValidationError("El stock máximo debe ser mayor o igual al stock mínimo")
        return stock_maximo
    
    def clean_punto_reorden(self):
        punto_reorden = self.cleaned_data.get('punto_reorden')
        stock_minimo = self.cleaned_data.get('stock_minimo')
        if punto_reorden is not None:
            if punto_reorden < 0:
                raise forms.ValidationError("El punto de reorden no puede ser negativo")
            if stock_minimo is not None and punto_reorden < stock_minimo:
                raise forms.ValidationError("El punto de reorden debe ser mayor o igual al stock mínimo")
        return punto_reorden
    
    def clean_imagen_url(self):
        imagen_url = self.cleaned_data.get('imagen_url')
        if imagen_url:
            if len(imagen_url) > 500:
                raise forms.ValidationError("La URL de la imagen no puede tener más de 500 caracteres")
            validator = URLValidator()
            try:
                validator(imagen_url)
            except forms.ValidationError:
                raise forms.ValidationError("La URL de la imagen no es válida")
        return imagen_url
    
    def clean_ficha_tecnica_url(self):
        ficha_tecnica_url = self.cleaned_data.get('ficha_tecnica_url')
        if ficha_tecnica_url:
            if len(ficha_tecnica_url) > 500:
                raise forms.ValidationError("La URL de la ficha técnica no puede tener más de 500 caracteres")
            validator = URLValidator()
            try:
                validator(ficha_tecnica_url)
            except forms.ValidationError:
                raise forms.ValidationError("La URL de la ficha técnica no es válida")
        return ficha_tecnica_url
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

