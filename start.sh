#!/bin/bash

# Script para iniciar la aplicación completa

echo "=== Chat IA Local - Iniciando aplicación ==="
echo ""

# Verificar si vLLM está corriendo
VLLM_PID=""
echo "🔍 Verificando vLLM..."
if ! curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
    echo "⚠️  Advertencia: vLLM no parece estar corriendo"
    echo "   Ejecuta primero: python3 Backend/setup_models.py"
    echo "   O inicia vLLM manualmente: vllm serve meta-llama/Llama-3.1-8B-Instruct"
    echo ""
    echo "   ¿Quieres iniciar vLLM ahora? (s/n)"
    read -r respuesta
    if [ "$respuesta" = "s" ]; then
        echo "🚀 Iniciando vLLM..."
        echo "   Esto puede tomar varios minutos la primera vez..."
        # Iniciar vLLM directamente en lugar de usar setup_models.py
        vllm serve meta-llama/Llama-3.1-8B-Instruct > /tmp/vllm.log 2>&1 &
        VLLM_PID=$!
        echo "⏳ Esperando a que vLLM esté listo (esto puede tomar varios minutos)..."
        # Esperar hasta que vLLM responda
        for i in {1..60}; do
            sleep 5
            if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
                echo "✅ vLLM está listo!"
                break
            fi
            echo "   Esperando... ($i/60)"
        done
    else
        echo "   Por favor inicia vLLM antes de continuar"
        exit 1
    fi
else
    echo "✅ vLLM está corriendo"
fi
echo ""

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

# Verificar Node.js y npm
echo "🔍 Verificando Node.js y npm..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    echo ""
    echo "📋 Para instalar Node.js en Kali Linux:"
    echo "   1. curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   2. sudo apt-get install -y nodejs"
    echo ""
    echo "   O usando nvm:"
    echo "   1. curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "   2. source ~/.bashrc"
    echo "   3. nvm install 18"
    echo ""
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado"
    echo ""
    echo "📋 npm generalmente viene con Node.js."
    echo "   Si Node.js está instalado pero npm no, intenta:"
    echo "   sudo apt-get install npm"
    echo ""
    exit 1
fi

echo "✅ Node.js $(node --version) y npm $(npm --version) detectados"
echo ""

# Configurar frontend
echo "🔧 Configurando frontend React..."
cd Frontend

# Verificar si node_modules existe, si no instalar dependencias
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias del frontend..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando dependencias del frontend"
        echo "   Intenta ejecutar manualmente: cd Frontend && npm install"
        cd ..
        exit 1
    fi
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
if command -v npm &> /dev/null; then
    npm start &
    FRONTEND_PID=$!
else
    echo "❌ npm no disponible para iniciar el frontend"
    FRONTEND_PID=""
fi
cd ..

echo ""
echo "✅ Aplicación iniciada!"
echo "   Backend: http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios"

# Esperar a que el usuario presione Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    if [ ! -z "$VLLM_PID" ]; then
        kill $VLLM_PID 2>/dev/null
    fi
    exit
}
trap cleanup INT TERM
wait

