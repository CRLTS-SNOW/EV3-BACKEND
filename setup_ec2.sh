#!/bin/bash

# Script de configuración para EC2 - Proyecto Lili's Backend
# Ejecutar en la instancia EC2 después de conectarse por SSH

set -e  # Salir si hay algún error

echo "=========================================="
echo "Configuración de EC2 - Proyecto Lili's"
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Limpiar proyecto anterior (si existe)
echo -e "${YELLOW}[1/10] Limpiando proyecto anterior...${NC}"
if [ -d "/home/ec2-user/EV3-BACKEND" ]; then
    echo "Eliminando proyecto anterior..."
    rm -rf /home/ec2-user/EV3-BACKEND
fi
if [ -d "/home/ec2-user/lilis-backend" ]; then
    echo "Eliminando proyecto anterior..."
    rm -rf /home/ec2-user/lilis-backend
fi
echo -e "${GREEN}✓ Limpieza completada${NC}"

# 2. Actualizar sistema
echo -e "${YELLOW}[2/10] Actualizando sistema...${NC}"
sudo dnf update -y
echo -e "${GREEN}✓ Sistema actualizado${NC}"

# 3. Instalar dependencias del sistema
echo -e "${YELLOW}[3/10] Instalando dependencias del sistema...${NC}"

# Python 3.11 y herramientas
sudo dnf install -y python3.11 python3.11-pip python3.11-devel gcc

# PostgreSQL
sudo dnf install -y postgresql15 postgresql15-server postgresql15-contrib

# Node.js 18.x
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo dnf install -y nodejs

# Git
sudo dnf install -y git

# Nginx
sudo dnf install -y nginx

# Otras herramientas útiles
sudo dnf install -y htop nano wget curl

echo -e "${GREEN}✓ Dependencias instaladas${NC}"

# 4. Configurar PostgreSQL
echo -e "${YELLOW}[4/10] Configurando PostgreSQL...${NC}"
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Crear usuario y base de datos
sudo -u postgres psql <<EOF
-- Crear usuario si no existe
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'lilis_user') THEN
    CREATE USER lilis_user WITH PASSWORD 'lilis_password_2024';
  END IF;
END
\$\$;

-- Crear base de datos si no existe
SELECT 'CREATE DATABASE lilis_db OWNER lilis_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lilis_db')\gexec

-- Dar permisos
GRANT ALL PRIVILEGES ON DATABASE lilis_db TO lilis_user;
\q
EOF

# Configurar PostgreSQL para aceptar conexiones locales
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /var/lib/pgsql/data/postgresql.conf
sudo systemctl restart postgresql

echo -e "${GREEN}✓ PostgreSQL configurado${NC}"

# 5. Instalar Python packages globales
echo -e "${YELLOW}[5/10] Instalando paquetes Python globales...${NC}"
sudo python3.11 -m pip install --upgrade pip
sudo python3.11 -m pip install virtualenv
echo -e "${GREEN}✓ Paquetes Python instalados${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Configuración inicial completada!"
echo "==========================================${NC}"
echo ""
echo "Próximos pasos:"
echo "1. Sube tu proyecto usando git clone o scp"
echo "2. Crea el archivo .env con las credenciales"
echo "3. Ejecuta el script setup_project.sh"
echo ""

