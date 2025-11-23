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
    phone = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
        help_text="Formato chileno (ej: +56912345678 o 912345678)"
    )
    photo = forms.ImageField(
        label="Foto",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        help_text="Tamaño recomendado: 200x200px. La imagen se redimensionará automáticamente."
    )

    nombres = forms.CharField(
        label="Nombres",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
        max_length=100,
        help_text="Nombres del usuario (requerido)"
    )
    apellidos = forms.CharField(
        label="Apellidos",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
        max_length=100,
        help_text="Apellidos del usuario (requerido)"
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=UserProfile.STATUS_CHOICES,
        initial='ACTIVO',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mfa_habilitado = forms.BooleanField(
        label="MFA Habilitado",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    area = forms.CharField(
        label="Área/Unidad",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        max_length=500
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            if profile.phone:
                self.fields['phone'].initial = profile.phone
            if profile.nombres:
                self.fields['nombres'].initial = profile.nombres
            if profile.apellidos:
                self.fields['apellidos'].initial = profile.apellidos
            if profile.estado:
                self.fields['estado'].initial = profile.estado
            if profile.mfa_habilitado:
                self.fields['mfa_habilitado'].initial = profile.mfa_habilitado
            if profile.area:
                self.fields['area'].initial = profile.area
            if profile.observaciones:
                self.fields['observaciones'].initial = profile.observaciones

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remover espacios y guiones
            phone_clean = phone.replace(' ', '').replace('-', '')
            # Validar formato internacional
            import re
            if not re.match(r'^\+?[1-9]\d{1,14}$', phone_clean):
                raise forms.ValidationError("El teléfono no es válido. Use formato internacional (ej: +56912345678)")
            return phone_clean
        return phone
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) < 3:
                raise forms.ValidationError("El usuario debe tener al menos 3 caracteres")
            if len(username) > 150:
                raise forms.ValidationError("El usuario no puede tener más de 150 caracteres")
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError("El usuario solo puede contener letras, números y guiones bajos")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if len(email) > 150:
                raise forms.ValidationError("El email no puede tener más de 150 caracteres")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        if password and len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

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
            profile.nombres = self.cleaned_data.get('nombres', '')
            profile.apellidos = self.cleaned_data.get('apellidos', '')
            profile.estado = self.cleaned_data.get('estado', 'ACTIVO')
            profile.mfa_habilitado = self.cleaned_data.get('mfa_habilitado', False)
            profile.area = self.cleaned_data.get('area', '')
            profile.observaciones = self.cleaned_data.get('observaciones', '')
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
    is_active = forms.BooleanField(
        required=False,
        label="Usuario Activo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    phone = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56912345678'}),
        help_text="Formato chileno (ej: +56912345678 o 912345678)"
    )
    photo = forms.ImageField(
        label="Foto",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    nombres = forms.CharField(
        label="Nombres",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
        max_length=100,
        help_text="Nombres del usuario (requerido)"
    )
    apellidos = forms.CharField(
        label="Apellidos",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
        max_length=100,
        help_text="Apellidos del usuario (requerido)"
    )
    estado = forms.ChoiceField(
        label="Estado",
        choices=UserProfile.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    mfa_habilitado = forms.BooleanField(
        label="MFA Habilitado",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    area = forms.CharField(
        label="Área/Unidad",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        max_length=500
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '100'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) < 3:
                raise forms.ValidationError("El usuario debe tener al menos 3 caracteres")
            if len(username) > 150:
                raise forms.ValidationError("El usuario no puede tener más de 150 caracteres")
            import re
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise forms.ValidationError("El usuario solo puede contener letras, números y guiones bajos")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if len(email) > 150:
                raise forms.ValidationError("El email no puede tener más de 150 caracteres")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['role'].initial = profile.role
            self.fields['estado'].initial = profile.estado
            self.fields['mfa_habilitado'].initial = profile.mfa_habilitado
            if profile.phone:
                self.fields['phone'].initial = profile.phone
            if profile.nombres:
                self.fields['nombres'].initial = profile.nombres
            if profile.apellidos:
                self.fields['apellidos'].initial = profile.apellidos
            if profile.area:
                self.fields['area'].initial = profile.area
            if profile.observaciones:
                self.fields['observaciones'].initial = profile.observaciones
        else:
            # Si no tiene perfil, crear uno por defecto
            if self.instance.pk:
                UserProfile.objects.get_or_create(user=self.instance, defaults={'role': 'ventas', 'estado': 'ACTIVO'})
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Actualizar perfil
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role', 'ventas')
            profile.nombres = self.cleaned_data.get('nombres', '') or ''
            profile.apellidos = self.cleaned_data.get('apellidos', '') or ''
            profile.estado = self.cleaned_data.get('estado', 'ACTIVO') or 'ACTIVO'
            profile.mfa_habilitado = self.cleaned_data.get('mfa_habilitado', False)
            profile.area = self.cleaned_data.get('area', '') or ''
            profile.observaciones = self.cleaned_data.get('observaciones', '') or ''
            
            # Manejar phone
            phone = self.cleaned_data.get('phone')
            if phone:
                profile.phone = phone
            else:
                profile.phone = None
            
            # Manejar photo
            photo = self.cleaned_data.get('photo')
            if photo:
                profile.photo = photo
            
            profile.save()
            # Nota: La sincronización con Firebase se hace en UserUpdateView.form_valid()
            # para tener mejor control y poder crear usuarios con contraseña por defecto
        return user

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remover espacios y guiones
            phone_clean = phone.replace(' ', '').replace('-', '')
            # Validar formato chileno: +56912345678, 56912345678, o 912345678
            import re
            # Debe empezar con +56, 56, o 9, seguido de 8 dígitos más (total 9 dígitos después del código de país)
            if not re.match(r'^(\+?56)?9\d{8}$', phone_clean):
                raise forms.ValidationError("El teléfono debe ser formato chileno (ej: +56912345678 o 912345678)")
            return phone_clean
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
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

