# Configurar Firebase para Restablecimiento de Contraseña

## 🔧 Pasos para Configurar

### 1. Autorizar Dominio en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto: **backend-proyecto-lilis**
3. Ve a **Authentication** > **Settings** (Configuración)
4. En la sección **Authorized domains** (Dominios autorizados), agrega:
   - `localhost`
   - `127.0.0.1`
   - Tu dominio de producción (si aplica)

### 2. Configurar Plantilla de Email

1. En Firebase Console, ve a **Authentication** > **Templates** (Plantillas)
2. Selecciona **Password reset** (Restablecer contraseña)
3. Personaliza el email (opcional):
   - **Subject**: "Restablece tu contraseña"
   - **Body**: Puedes usar el template por defecto o personalizarlo
4. Haz clic en **Save** (Guardar)

### 3. Verificar Configuración de Email

1. Ve a **Authentication** > **Settings** > **Users** (Usuarios)
2. Verifica que **Email link (password reset)** esté habilitado
3. Verifica que **Email/Password** esté habilitado como método de autenticación

## 🧪 Probar el Restablecimiento

1. Abre la aplicación en `http://localhost:8000` o `http://127.0.0.1:8000`
2. Haz clic en "¿Olvidaste tu contraseña?"
3. Ingresa un email que exista en Firebase (ej: `carlos.vivanco.08@gmail.com`)
4. Revisa tu bandeja de entrada **y la carpeta de spam**

## ❓ Problemas Comunes

### No llega el correo

**Solución:**
1. ✅ Verifica que el dominio esté autorizado (paso 1)
2. ✅ Revisa la carpeta de spam
3. ✅ Verifica que el email exista en Firebase Authentication
4. ✅ Espera unos minutos (puede tardar)
5. ✅ Verifica la consola del navegador para errores

### Error: "auth/unauthorized-domain"

**Solución:**
- Agrega `localhost` y `127.0.0.1` a los dominios autorizados en Firebase

### Error: "auth/unauthorized-continue-uri"

**Solución:**
1. Para desarrollo local (localhost/127.0.0.1), el código ya está configurado para NO usar actionCodeSettings
2. Si aún tienes problemas:
   - Ve a Firebase Console > Authentication > Settings > Authorized domains
   - Asegúrate de que `localhost` y `127.0.0.1` estén en la lista
   - En Authentication > Templates > Password reset, configura la URL de redirección:
     - Para desarrollo: `http://localhost:8000` o `http://127.0.0.1:8000`
     - Para producción: tu dominio real

### Error: "auth/user-not-found"

**Solución:**
- El email no existe en Firebase. Usa un email que esté sincronizado:
  - `carlos.vivanco.08@gmail.com` (admin)
  - `bodega@demo.com` (bodeguero)
  - `ventas@demo.com` (vendedor)

## 📧 Verificar Usuarios en Firebase

1. Ve a **Authentication** > **Users**
2. Deberías ver los 3 usuarios:
   - admin (carlos.vivanco.08@gmail.com)
   - bodeguero (bodega@demo.com)
   - vendedor (ventas@demo.com)

## 🔐 Notas Importantes

- Los correos pueden tardar unos minutos en llegar
- Revisa siempre la carpeta de spam
- El enlace de restablecimiento expira después de cierto tiempo
- Solo funciona con emails que estén en Firebase Authentication

