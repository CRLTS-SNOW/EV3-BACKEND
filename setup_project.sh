#!/bin/bash

# Script para configurar el proyecto después de subirlo a EC2
# Ejecutar desde el directorio del proyecto en EC2

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/ec2-user/EV3-BACKEND"

echo -e "${YELLOW}[1/8] Creando entorno virtual...${NC}"
cd $PROJECT_DIR
python3.11 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Entorno virtual creado${NC}"

echo -e "${YELLOW}[2/8] Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencias Python instaladas${NC}"

echo -e "${YELLOW}[3/8] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cat > .env <<EOF
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DATABASE_URL=postgresql://lilis_user:lilis_password_2024@localhost:5432/lilis_db
ALLOWED_HOSTS=ec2-98-95-67-251.compute-1.amazonaws.com,localhost,127.0.0.1

# Firebase
FIREBASE_PROJECT_ID=backend-proyecto-lilis
FIREBASE_WEB_API_KEY=AIzaSyBBaZY2-tp24fMt3uc13gLRpu9KnGOFA9g
FRONTEND_URL=http://ec2-98-95-67-251.compute-1.amazonaws.com

# Email (configurar según necesidad)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠ IMPORTANTE: Edita el archivo .env con tus credenciales reales${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi

echo -e "${YELLOW}[4/8] Ejecutando migraciones...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Migraciones completadas${NC}"

echo -e "${YELLOW}[5/8] Creando superusuario (si no existe)...${NC}"
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@lilis.com', '123456')
    print('Superusuario creado: admin / 123456')
else:
    print('Superusuario ya existe')
EOF
echo -e "${GREEN}✓ Superusuario configurado${NC}"

echo -e "${YELLOW}[6/8] Aplicando semillas de datos...${NC}"
if [ -f "gestion/management/commands/seed_data.py" ]; then
    python manage.py seed_data
fi
if [ -f "gestion/management/commands/seed_inventory.py" ]; then
    python manage.py seed_inventory
fi
if [ -f "gestion/management/commands/seed_warehouses.py" ]; then
    python manage.py seed_warehouses
fi
echo -e "${GREEN}✓ Semillas aplicadas${NC}"

echo -e "${YELLOW}[7/8] Instalando dependencias del frontend...${NC}"
cd frontend
npm install
echo -e "${GREEN}✓ Dependencias del frontend instaladas${NC}"

echo -e "${YELLOW}[8/8] Construyendo frontend para producción...${NC}"
# Actualizar API_BASE_URL en el código antes de construir
sed -i "s|const API_BASE_URL = .*|const API_BASE_URL = 'http://ec2-98-95-67-251.compute-1.amazonaws.com/api';|g" src/services/api.js
npm run build
echo -e "${GREEN}✓ Frontend construido${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Configuración del proyecto completada!"
echo "==========================================${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Configurar Firebase con la nueva URL"
echo "2. Configurar Nginx para servir la aplicación"
echo "3. Configurar Gunicorn para el backend"
echo "4. Iniciar los servicios"
echo ""

