#!/bin/bash

# Script para iniciar la aplicación completa

echo "=== Chat IA Local - Iniciando aplicación ==="
echo ""

# Verificar si vLLM está corriendo
VLLM_PID=""
LLAMA_MODEL="meta-llama/Llama-3.1-8B-Instruct"

echo "🔍 Verificando vLLM..."
if ! curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
    echo "⚠️  vLLM no está corriendo"
    echo ""
    
    # Verificar si huggingface-cli está instalado y funcionando
    HF_CLI_CMD=""
    if command -v huggingface-cli &> /dev/null; then
        HF_CLI_CMD="huggingface-cli"
    elif python3 -m huggingface_hub.cli &> /dev/null 2>&1; then
        HF_CLI_CMD="python3 -m huggingface_hub.cli"
    else
        echo "📦 Instalando huggingface_hub..."
        python3 -m pip install --quiet --user huggingface_hub
        # Verificar nuevamente después de instalar
        if command -v huggingface-cli &> /dev/null; then
            HF_CLI_CMD="huggingface-cli"
        elif python3 -m huggingface_hub.cli &> /dev/null 2>&1; then
            HF_CLI_CMD="python3 -m huggingface_hub.cli"
        else
            echo "⚠️  No se pudo instalar huggingface-cli correctamente"
            echo "   Intentando método alternativo con token..."
            HF_CLI_CMD=""
        fi
    fi
    
    # Verificar si el usuario está logueado en Hugging Face
    HF_TOKEN_FILE="$HOME/.huggingface/token"
    if [ ! -f "$HF_TOKEN_FILE" ]; then
        echo "🔐 No estás autenticado en Hugging Face"
        echo "   Se necesitan credenciales para descargar los modelos"
        echo ""
        read -p "   Email de Hugging Face: " HF_EMAIL
        read -sp "   Contraseña: " HF_PASSWORD
        echo ""
        echo ""
        echo "🔑 Autenticando en Hugging Face..."
        
        # Intentar login con huggingface-cli si está disponible
        if [ ! -z "$HF_CLI_CMD" ]; then
            echo "$HF_PASSWORD" | $HF_CLI_CMD login --username "$HF_EMAIL" --password-stdin 2>&1
            
            if [ $? -ne 0 ]; then
                echo "⚠️  Error en la autenticación con CLI. Usando método alternativo..."
                HF_CLI_CMD=""
            else
                echo "✅ Autenticación exitosa"
            fi
        fi
        
        # Si el CLI falló o no está disponible, usar token directamente
        if [ -z "$HF_CLI_CMD" ] || [ ! -f "$HF_TOKEN_FILE" ]; then
            echo ""
            echo "   Método alternativo: usar token de Hugging Face"
            echo "   Puedes obtenerlo en: https://huggingface.co/settings/tokens"
            read -sp "   Token de Hugging Face (o Enter para continuar sin token): " HF_TOKEN
            echo ""
            if [ ! -z "$HF_TOKEN" ]; then
                mkdir -p "$HOME/.huggingface"
                echo "$HF_TOKEN" > "$HF_TOKEN_FILE"
                echo "✅ Token guardado"
            else
                echo "⚠️  Continuando sin token. Los modelos públicos deberían funcionar."
            fi
        fi
    else
        echo "✅ Ya estás autenticado en Hugging Face"
    fi
    
    echo ""
    echo "🚀 Iniciando vLLM con modelo: $LLAMA_MODEL"
    echo "   Esto puede tomar varios minutos la primera vez (descargará el modelo)..."
    echo ""
    
    # Iniciar vLLM en background
    vllm serve "$LLAMA_MODEL" > /tmp/vllm.log 2>&1 &
    VLLM_PID=$!
    
    echo "⏳ Esperando a que vLLM esté listo..."
    echo "   (Revisa /tmp/vllm.log para ver el progreso de descarga)"
    echo ""
    
    # Esperar hasta que vLLM responda (más tiempo para la primera descarga)
    for i in {1..120}; do
        sleep 5
        if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
            echo "✅ vLLM está listo!"
            break
        fi
        if [ $((i % 6)) -eq 0 ]; then
            echo "   Esperando... ($i/120) - Esto puede tardar si es la primera descarga"
        fi
    done
    
    # Verificar si vLLM está corriendo después de la espera
    if ! curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
        echo ""
        echo "⚠️  vLLM no respondió después de esperar"
        echo "   Revisa los logs en /tmp/vllm.log para ver qué pasó"
        echo "   Puede que el modelo esté descargándose aún..."
        echo ""
        echo "   ¿Quieres continuar de todas formas? (s/n)"
        read -r continuar
        if [ "$continuar" != "s" ]; then
            kill $VLLM_PID 2>/dev/null
            exit 1
        fi
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

