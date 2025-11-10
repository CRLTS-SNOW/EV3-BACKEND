# gestion/forms/user_forms.py

from django import forms
from django.contrib.auth.models import User
from ..models import UserProfile, Warehouse

class UserCreateForm(forms.ModelForm):
    """
    Formulario para crear usuarios con rol.
    """
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Mínimo 8 caracteres"
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        label="Rol",
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        label="Bodega Asignada",
        help_text="Solo para Operador de Bodega",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +1234567890'})
    )
    photo = forms.ImageField(
        label="Foto",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text="Tamaño recomendado: 200x200px. La imagen se redimensionará automáticamente."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'profile'):
            if self.instance.profile.phone:
                self.fields['phone'].initial = self.instance.profile.phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        role = cleaned_data.get('role')
        warehouse = cleaned_data.get('warehouse')

        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Si es bodega, debe tener bodega asignada
        if role == 'bodega' and not warehouse:
            raise forms.ValidationError("Los Operadores de Bodega deben tener una bodega asignada.")
        
        # Si no es bodega, no debe tener bodega
        if role != 'bodega' and warehouse:
            cleaned_data['warehouse'] = None

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        # NO establecer contraseña en Django - solo usar Firebase
        # user.set_password(password)  # COMENTADO - solo Firebase
        if commit:
            user.save()
            # Crear o actualizar el perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            if self.cleaned_data.get('warehouse'):
                profile.warehouse = self.cleaned_data['warehouse']
            if self.cleaned_data.get('phone'):
                profile.phone = self.cleaned_data['phone']
            if self.cleaned_data.get('photo'):
                profile.photo = self.cleaned_data['photo']
            profile.save()
            
            # Sincronizar con Firebase si tiene email (esto creará el usuario en Firebase con la contraseña)
            if user.email:
                try:
                    from gestion.firebase_service import sync_django_user_to_firebase
                    sync_django_user_to_firebase(user, password=password)
                except Exception as e:
                    # No fallar si Firebase no está configurado
                    pass
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Formulario para actualizar usuarios (sin cambiar contraseña).
    """
    role = forms.ChoiceField(
        label="Rol",
        choices=UserProfile.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all(),
        required=False,
        label="Bodega Asignada",
        help_text="Solo para Operador de Bodega",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    is_active = forms.BooleanField(
        required=False,
        label="Usuario Activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    phone = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +1234567890'})
    )
    photo = forms.ImageField(
        label="Foto",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['role'].initial = self.instance.profile.role
            if self.instance.profile.warehouse:
                self.fields['warehouse'].initial = self.instance.profile.warehouse.id
            if self.instance.profile.phone:
                self.fields['phone'].initial = self.instance.profile.phone
        else:
            # Si no tiene perfil, crear uno por defecto
            if self.instance.pk:
                UserProfile.objects.get_or_create(user=self.instance, defaults={'role': 'ventas'})
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Actualizar perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            if self.cleaned_data.get('warehouse'):
                profile.warehouse = self.cleaned_data['warehouse']
            else:
                profile.warehouse = None
            if self.cleaned_data.get('phone'):
                profile.phone = self.cleaned_data['phone']
            if self.cleaned_data.get('photo'):
                profile.photo = self.cleaned_data['photo']
            profile.save()
            # Nota: La sincronización con Firebase se hace en UserUpdateView.form_valid()
            # para tener mejor control y poder crear usuarios con contraseña por defecto
        return user

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        warehouse = cleaned_data.get('warehouse')

        # Si es bodega, debe tener bodega asignada
        if role == 'bodega' and not warehouse:
            raise forms.ValidationError("Los Operadores de Bodega deben tener una bodega asignada.")
        
        # Si no es bodega, no debe tener bodega
        if role != 'bodega' and warehouse:
            cleaned_data['warehouse'] = None

        return cleaned_data

class UserPasswordChangeForm(forms.Form):
    """
    Formulario para cambiar la contraseña de un usuario.
    Solo requiere la nueva contraseña si es el mismo usuario cambiando su contraseña.
    Si es un admin cambiando la contraseña de otro usuario, no requiere la contraseña actual.
    """
    current_password = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Solo requerida si estás cambiando tu propia contraseña"
    )
    new_password = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Mínimo 8 caracteres"
    )
    new_password_confirm = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        # Extraer user e is_own_password de kwargs antes de pasar a super()
        user = kwargs.pop('user', None)
        is_own_password = kwargs.pop('is_own_password', False)
        
        super().__init__(*args, **kwargs)
        self.user = user
        self.is_own_password = is_own_password
        if not is_own_password:
            # Si es un admin cambiando la contraseña de otro usuario, ocultar campo de contraseña actual
            self.fields['current_password'].widget = forms.HiddenInput()
            self.fields['current_password'].required = False
        else:
            self.fields['current_password'].required = True

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        current_password = cleaned_data.get('current_password')

        # Validar que las nuevas contraseñas coincidan
        if new_password != new_password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        if len(new_password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # Si es el usuario cambiando su propia contraseña, validar contraseña actual en Firebase
        if self.is_own_password and self.user and self.user.email:
            if not current_password:
                raise forms.ValidationError("Debes ingresar tu contraseña actual.")
            # Verificar contraseña actual en Firebase (no en Django)
            from gestion.firebase_service import verify_firebase_password
            firebase_result = verify_firebase_password(self.user.email, current_password)
            if not firebase_result.get('success'):
                error_msg = firebase_result.get('error', 'Contraseña incorrecta')
                if 'INVALID_PASSWORD' in error_msg or 'INVALID_LOGIN_CREDENTIALS' in error_msg or 'EMAIL_NOT_FOUND' in error_msg:
                    raise forms.ValidationError("La contraseña actual es incorrecta.")
                else:
                    raise forms.ValidationError(f"Error al verificar la contraseña: {error_msg}")

        return cleaned_data

