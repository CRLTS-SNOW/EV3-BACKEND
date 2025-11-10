# Solución: Error "unauthorized-continue-uri" en Firebase

## ✅ Solución Implementada

El código ahora detecta si estás en localhost y **NO usa actionCodeSettings**, lo que evita el error de URL no autorizada.

## 🔧 Configuración Adicional en Firebase (Opcional)

Si aún tienes problemas, sigue estos pasos:

### 1. Autorizar Dominios en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto: **backend-proyecto-lilis**
3. Ve a **Authentication** > **Settings** (Configuración)
4. En la sección **Authorized domains**, verifica que estén:
   - `localhost` (debería estar por defecto)
   - `127.0.0.1`
   - Tu dominio de producción (si aplica)

### 2. Configurar URL de Redirección en la Plantilla de Email

1. Ve a **Authentication** > **Templates** (Plantillas)
2. Selecciona **Password reset** (Restablecer contraseña)
3. En **Action URL**, configura:
   - Para desarrollo: `http://localhost:8000` o `http://127.0.0.1:8000`
   - Para producción: tu dominio real
4. Haz clic en **Save** (Guardar)

## 🧪 Probar Ahora

1. Recarga la página de login
2. Haz clic en "¿Olvidaste tu contraseña?"
3. Ingresa: `carlos.vivanco.08@gmail.com`
4. Debería funcionar sin errores

## 📝 Notas

- El código ahora detecta automáticamente si estás en localhost
- En localhost, no se usa `actionCodeSettings`, evitando el error
- En producción, se usa `actionCodeSettings` con la URL configurada
- El email debería llegar a la bandeja de entrada (revisa spam también)

## ❓ Si Aún No Funciona

1. Verifica que el email `carlos.vivanco.08@gmail.com` exista en Firebase:
   - Ve a **Authentication** > **Users**
   - Busca el usuario con ese email

2. Verifica la consola del navegador (F12) para ver si hay otros errores

3. Espera unos minutos - los emails pueden tardar en llegar

4. Revisa la carpeta de spam

