#!/bin/bash

# Script para iniciar la aplicación completa

echo "=== Chat IA Local - Iniciando aplicación ==="
echo ""

# Verificar si Ollama está corriendo
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Advertencia: Ollama no parece estar corriendo"
    echo "   Inicia Ollama con: ollama serve"
    echo ""
fi

# Configurar backend
echo "🔧 Configurando backend Flask..."
cd Backend

# Verificar si existe venv, si no crearlo
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar venv
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar/actualizar dependencias del backend
echo "📦 Instalando dependencias del backend..."
pip install -r requirements.txt

cd ..

# Configurar frontend
echo "🔧 Configurando frontend React..."
cd Frontend

# Verificar si node_modules existe, si no instalar dependencias
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias del frontend..."
    npm install
else
    echo "✅ Dependencias del frontend ya instaladas"
fi

cd ..

# Iniciar backend con venv activo
echo ""
echo "🚀 Iniciando backend Flask..."
cd Backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Esperar a que el backend esté listo
echo "⏳ Esperando a que el backend esté listo..."
sleep 3

# Iniciar frontend
echo "🚀 Iniciando frontend React..."
cd Frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Aplicación iniciada!"
echo "   Backend: http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios"

# Esperar a que el usuario presione Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

