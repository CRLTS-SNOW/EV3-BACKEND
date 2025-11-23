#!/bin/bash

# Script para configurar Nginx y Gunicorn
# Ejecutar después de setup_project.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/ec2-user/EV3-BACKEND"

echo -e "${YELLOW}[1/4] Instalando Gunicorn...${NC}"
cd $PROJECT_DIR
source venv/bin/activate
pip install gunicorn
echo -e "${GREEN}✓ Gunicorn instalado${NC}"

echo -e "${YELLOW}[2/4] Creando servicio systemd para Gunicorn...${NC}"
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
echo -e "${GREEN}✓ Servicio Gunicorn configurado y iniciado${NC}"

echo -e "${YELLOW}[3/4] Configurando Nginx...${NC}"
sudo tee /etc/nginx/conf.d/lilis.conf > /dev/null <<EOF
server {
    listen 80;
    server_name ec2-98-95-67-251.compute-1.amazonaws.com;

    client_max_body_size 100M;

    # Servir archivos estáticos del frontend
    location / {
        root $PROJECT_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
        index index.html;
    }

    # API del backend
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Archivos estáticos de Django (admin, etc.)
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
    }

    # Archivos media de Django
    location /media/ {
        alias $PROJECT_DIR/media/;
    }
}
EOF

# Recolectar archivos estáticos de Django
cd $PROJECT_DIR
source venv/bin/activate
python manage.py collectstatic --noinput

# Verificar configuración de Nginx
sudo nginx -t

# Iniciar Nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx configurado y reiniciado${NC}"

echo -e "${YELLOW}[4/4] Configurando firewall...${NC}"
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
echo -e "${GREEN}✓ Firewall configurado${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Configuración de servidor completada!"
echo "==========================================${NC}"
echo ""
echo "Servicios iniciados:"
echo "- Gunicorn (Backend Django)"
echo "- Nginx (Servidor web)"
echo ""
echo "Verifica el estado con:"
echo "  sudo systemctl status lilis-backend"
echo "  sudo systemctl status nginx"
echo ""

