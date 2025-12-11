#!/bin/bash

# Script para iniciar solo el backend con venv activo

cd "$(dirname "$0")"

# Verificar si existe venv, si no crearlo
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar venv
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip si es necesario
pip install --upgrade pip --quiet

# Instalar/actualizar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Iniciar aplicación
echo "🚀 Iniciando backend Flask..."
python app.py

