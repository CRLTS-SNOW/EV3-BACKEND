from django.contrib import admin
from django.urls import path, include

# --- 1. Importa las vistas de autenticación de Django ---
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- 2. Esta es tu app, como ya la tenías ---
    path('app/', include('gestion.urls')),

    # --- 3. AÑADE LAS NUEVAS RUTAS DE LOGIN Y LOGOUT ---
    
    # URL de Login (la raíz del sitio)
    path('', auth_views.LoginView.as_view(
        # Le decimos a Django que use nuestro template personalizado
        template_name='gestion/login.html'
    ), name='login'),
    
    # URL de Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
