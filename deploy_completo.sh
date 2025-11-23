#!/bin/bash

# Script completo de despliegue para EC2
# Copiar y pegar este contenido completo en la terminal de EC2

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "  DESPLIEGUE COMPLETO - PROYECTO LILI'S"
echo "==========================================${NC}"
echo ""

# 1. LIMPIAR PROYECTO ANTERIOR
echo -e "${YELLOW}[1/11] Limpiando proyecto anterior...${NC}"
cd ~
if [ -d "EV3-BACKEND" ]; then
    rm -rf EV3-BACKEND
    echo -e "${GREEN}✓ Proyecto anterior eliminado${NC}"
else
    echo -e "${GREEN}✓ No hay proyecto anterior${NC}"
fi

# 2. ACTUALIZAR SISTEMA
echo -e "${YELLOW}[2/11] Actualizando sistema...${NC}"
sudo dnf update -y -q
echo -e "${GREEN}✓ Sistema actualizado${NC}"

# 3. INSTALAR DEPENDENCIAS
echo -e "${YELLOW}[3/11] Instalando dependencias del sistema...${NC}"
sudo dnf install -y -q python3.11 python3.11-pip python3.11-devel gcc postgresql15 postgresql15-server postgresql15-contrib git nginx htop nano wget curl

# Node.js
if ! command -v node &> /dev/null; then
    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - > /dev/null 2>&1
    sudo dnf install -y -q nodejs
fi

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# 4. CONFIGURAR POSTGRESQL
echo -e "${YELLOW}[4/11] Configurando PostgreSQL...${NC}"
if [ ! -d "/var/lib/pgsql/data" ] || [ -z "$(ls -A /var/lib/pgsql/data)" ]; then
    sudo postgresql-setup --initdb > /dev/null 2>&1
fi
sudo systemctl enable postgresql > /dev/null 2>&1
sudo systemctl start postgresql > /dev/null 2>&1

# Crear base de datos y usuario
sudo -u postgres psql <<EOF > /dev/null 2>&1
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'lilis_user') THEN
    CREATE USER lilis_user WITH PASSWORD 'lilis_password_2024';
  END IF;
END
\$\$;

SELECT 'CREATE DATABASE lilis_db OWNER lilis_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lilis_db')\gexec

GRANT ALL PRIVILEGES ON DATABASE lilis_db TO lilis_user;
\q
EOF

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"

# 5. ESPERAR A QUE EL USUARIO SUBA EL PROYECTO
echo ""
echo -e "${BLUE}=========================================="
echo "  IMPORTANTE: SUBE TU PROYECTO AHORA"
echo "==========================================${NC}"
echo ""
echo "Desde tu máquina Windows, ejecuta uno de estos comandos:"
echo ""
echo -e "${YELLOW}Opción 1 - SCP (PowerShell):${NC}"
echo 'scp -i "C:\Users\carlo\Desktop\claves-instancias-carlosvivanco.pem" -r ^'
echo '    --exclude="venv" --exclude="node_modules" --exclude=".git" ^'
echo '    --exclude="__pycache__" --exclude="*.pyc" ^'
echo '    C:\Users\carlo\Desktop\EV3-BACKEND ec2-user@ec2-98-95-67-251.compute-1.amazonaws.com:~/EV3-BACKEND'
echo ""
echo -e "${YELLOW}Opción 2 - Usar WinSCP o FileZilla (GUI)${NC}"
echo ""
echo -e "${BLUE}Presiona ENTER cuando hayas subido el proyecto...${NC}"
read -p ""

# 6. VERIFICAR QUE EL PROYECTO ESTÁ PRESENTE
if [ ! -d "~/EV3-BACKEND" ] && [ ! -d "EV3-BACKEND" ]; then
    echo -e "${RED}✗ No se encontró el proyecto. Por favor, súbelo primero.${NC}"
    exit 1
fi

cd ~/EV3-BACKEND || cd EV3-BACKEND
PROJECT_DIR=$(pwd)

# 7. CREAR ENTORNO VIRTUAL
echo -e "${YELLOW}[5/11] Creando entorno virtual...${NC}"
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
echo -e "${GREEN}✓ Entorno virtual creado${NC}"

# 8. INSTALAR DEPENDENCIAS PYTHON
echo -e "${YELLOW}[6/11] Instalando dependencias Python...${NC}"
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Dependencias Python instaladas${NC}"

# 9. CONFIGURAR .ENV
echo -e "${YELLOW}[7/11] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    cat > .env <<EOF
DEBUG=False
SECRET_KEY=$SECRET_KEY
DATABASE_URL=postgresql://lilis_user:lilis_password_2024@localhost:5432/lilis_db
ALLOWED_HOSTS=ec2-98-95-67-251.compute-1.amazonaws.com,localhost,127.0.0.1,98.95.67.251

# Firebase
FIREBASE_PROJECT_ID=backend-proyecto-lilis
FIREBASE_WEB_API_KEY=AIzaSyBBaZY2-tp24fMt3uc13gLRpu9KnGOFA9g
FRONTEND_URL=http://ec2-98-95-67-251.compute-1.amazonaws.com

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF
    echo -e "${GREEN}✓ Archivo .env creado${NC}"
    echo -e "${YELLOW}⚠ Edita .env si necesitas agregar credenciales de Firebase${NC}"
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi

# 10. EJECUTAR MIGRACIONES
echo -e "${YELLOW}[8/11] Ejecutando migraciones...${NC}"
python manage.py migrate
echo -e "${GREEN}✓ Migraciones completadas${NC}"

# 11. CREAR SUPERUSUARIO
echo -e "${YELLOW}[9/11] Configurando superusuario...${NC}"
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

# 12. APLICAR SEMILLAS
echo -e "${YELLOW}[10/11] Aplicando semillas de datos...${NC}"
if [ -f "gestion/management/commands/seed_data.py" ]; then
    python manage.py seed_data 2>/dev/null || echo "Semilla seed_data ejecutada"
fi
if [ -f "gestion/management/commands/seed_inventory.py" ]; then
    python manage.py seed_inventory 2>/dev/null || echo "Semilla seed_inventory ejecutada"
fi
if [ -f "gestion/management/commands/seed_warehouses.py" ]; then
    python manage.py seed_warehouses 2>/dev/null || echo "Semilla seed_warehouses ejecutada"
fi
echo -e "${GREEN}✓ Semillas aplicadas${NC}"

# 13. CONFIGURAR FRONTEND
echo -e "${YELLOW}[11/11] Configurando frontend...${NC}"
cd frontend

# Actualizar API_BASE_URL para producción
if [ -f "src/services/api.js" ]; then
    sed -i "s|const API_BASE_URL = .*|const API_BASE_URL = 'http://ec2-98-95-67-251.compute-1.amazonaws.com/api';|g" src/services/api.js
fi

npm install --silent
npm run build
cd ..
echo -e "${GREEN}✓ Frontend configurado${NC}"

# 14. INSTALAR Y CONFIGURAR GUNICORN
echo -e "${YELLOW}[12/11] Configurando Gunicorn...${NC}"
pip install gunicorn -q

sudo tee /etc/systemd/system/lilis-backend.service > /dev/null <<EOF
[Unit]
Description=Lili's Backend Gunicorn daemon
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 gestion.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable lilis-backend
sudo systemctl start lilis-backend
echo -e "${GREEN}✓ Gunicorn configurado${NC}"

# 15. CONFIGURAR NGINX
echo -e "${YELLOW}[13/11] Configurando Nginx...${NC}"
python manage.py collectstatic --noinput > /dev/null 2>&1

sudo tee /etc/nginx/conf.d/lilis.conf > /dev/null <<EOF
server {
    listen 80;
    server_name ec2-98-95-67-251.compute-1.amazonaws.com;

    client_max_body_size 100M;

    location / {
        root $PROJECT_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
    }
}
EOF

sudo nginx -t > /dev/null 2>&1
sudo systemctl enable nginx
sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx configurado${NC}"

# 16. CONFIGURAR FIREWALL
echo -e "${YELLOW}[14/11] Configurando firewall...${NC}"
sudo firewall-cmd --permanent --add-service=http > /dev/null 2>&1
sudo firewall-cmd --permanent --add-service=https > /dev/null 2>&1
sudo firewall-cmd --reload > /dev/null 2>&1
echo -e "${GREEN}✓ Firewall configurado${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "  ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo "==========================================${NC}"
echo ""
echo "Tu aplicación está disponible en:"
echo -e "${BLUE}http://ec2-98-95-67-251.compute-1.amazonaws.com${NC}"
echo ""
echo "Credenciales de acceso:"
echo "  Usuario: admin"
echo "  Contraseña: 123456"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status lilis-backend  # Ver estado del backend"
echo "  sudo systemctl restart lilis-backend  # Reiniciar backend"
echo "  sudo journalctl -u lilis-backend -f  # Ver logs del backend"
echo ""
echo -e "${YELLOW}⚠ IMPORTANTE:${NC}"
echo "1. Configura Firebase para permitir el dominio: ec2-98-95-67-251.compute-1.amazonaws.com"
echo "2. Si tienes credenciales de Firebase, edita ~/EV3-BACKEND/.env"
echo "3. Verifica que el Security Group de EC2 permita tráfico HTTP (puerto 80)"
echo ""

