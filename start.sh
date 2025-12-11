#!/bin/bash

# Script para iniciar la aplicación completa con Ollama

echo "=== GP-Test - Iniciando aplicación ==="
echo ""

# Verificar e instalar Ollama
OLLAMA_PID=""
LLAMA_MODEL="llama3.2"
DEEPSEEK_MODEL="deepseek-coder"

echo "🔍 Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama no está instalado. Instalando..."
    echo ""
    echo "   Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    
    if [ $? -ne 0 ]; then
        echo "❌ Error instalando Ollama"
        echo "   Instala manualmente desde: https://ollama.com"
        exit 1
    fi
    
    echo "✅ Ollama instalado"
else
    echo "✅ Ollama está instalado"
fi

# Verificar si el servicio Ollama está corriendo
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "🚀 Iniciando servicio Ollama..."
    ollama serve > /tmp/ollama.log 2>&1 &
    OLLAMA_PID=$!
    sleep 3
    
    # Verificar que se inició correctamente
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "⚠️  El servicio Ollama no se inició correctamente"
        echo "   Intenta iniciarlo manualmente: ollama serve"
        exit 1
    fi
    echo "✅ Servicio Ollama iniciado"
else
    echo "✅ Servicio Ollama ya está corriendo"
fi

# Verificar si los modelos están descargados
echo ""
echo "🔍 Verificando modelos..."
MODELS=$(ollama list 2>/dev/null | grep -E "$LLAMA_MODEL|$DEEPSEEK_MODEL" || echo "")

if ! echo "$MODELS" | grep -q "$LLAMA_MODEL"; then
    echo "📥 Descargando modelo Llama: $LLAMA_MODEL"
    echo "   Esto puede tomar varios minutos la primera vez..."
    ollama pull "$LLAMA_MODEL"
    if [ $? -ne 0 ]; then
        echo "⚠️  Error descargando modelo Llama"
        echo "   Intenta manualmente: ollama pull $LLAMA_MODEL"
    else
        echo "✅ Modelo Llama descargado"
    fi
else
    echo "✅ Modelo Llama ya está disponible"
fi

if ! echo "$MODELS" | grep -q "$DEEPSEEK_MODEL"; then
    echo "📥 Descargando modelo DeepSeek: $DEEPSEEK_MODEL"
    echo "   Esto puede tomar varios minutos la primera vez..."
    ollama pull "$DEEPSEEK_MODEL"
    if [ $? -ne 0 ]; then
        echo "⚠️  Error descargando modelo DeepSeek"
        echo "   Intenta manualmente: ollama pull $DEEPSEEK_MODEL"
    else
        echo "✅ Modelo DeepSeek descargado"
    fi
else
    echo "✅ Modelo DeepSeek ya está disponible"
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
echo "   Ollama: http://localhost:11434"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"

# Esperar a que el usuario presione Ctrl+C
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    if [ ! -z "$OLLAMA_PID" ]; then
        kill $OLLAMA_PID 2>/dev/null
    fi
    exit
}
trap cleanup INT TERM
wait
