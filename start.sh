#!/bin/bash

# Script para iniciar la aplicación completa con Ollama

echo "=== GP-Test - Iniciando aplicación ==="
echo ""

# Verificar e instalar Ollama
OLLAMA_PID=""
# Modelos SIN restricciones de seguridad (optimizado para 25GB RAM)
# 
# MODELOS 7B (~4GB RAM cada uno) - Balance perfecto:
# 1. mistral:7b - Muy permisivo, excelente rendimiento - RECOMENDADO
# 2. qwen2:7b - Modelo chino, muy permisivo
# 3. llama2:7b - Llama 2 sin restricciones de Llama 3
# 4. codellama:7b - Enfocado en código, menos restrictivo
#
# MODELOS 13B (~16-20GB RAM cada uno) - Máximo rendimiento con 25GB:
# 5. mistral-nemo:12b - Versión más grande de Mistral (~12GB RAM)
# 6. qwen2:14b - Modelo chino más grande (~14GB RAM)
# 7. llama2:13b - Llama 2 más grande (~16GB RAM)
# 8. codellama:13b - CodeLlama más grande (~16GB RAM)
#
# Con 25GB RAM puedes usar modelos 7B sin problemas (recomendado)
# O modelos 13B si quieres máximo rendimiento (cambia las variables abajo)
LLAMA_MODEL="mistral:7b"  # Mistral 7B - muy permisivo y sin restricciones
DEEPSEEK_MODEL="codellama:7b"  # CodeLlama 7B - menos restrictivo que DeepSeek
# 
# Si quieres MÁXIMO rendimiento con 25GB RAM, descomenta estas líneas:
# LLAMA_MODEL="mistral-nemo:12b"  # ~12GB RAM, más potente
# DEEPSEEK_MODEL="codellama:13b"  # ~16GB RAM, más potente para código

echo "🔍 Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "📦 Ollama no está instalado"
    echo ""
    echo "   Intentando instalar Ollama..."
    echo "   (Esto puede tardar si hay problemas de conexión)"
    
    # Intentar instalación con timeout más largo y reintentos
    if curl --connect-timeout 30 --max-time 300 -fsSL https://ollama.com/install.sh | sh 2>&1; then
        echo "✅ Ollama instalado correctamente"
    else
        echo ""
        echo "⚠️  Error instalando Ollama automáticamente"
        echo ""
        echo "📋 Opciones para instalar Ollama manualmente:"
        echo ""
        echo "   Opción 1: Descargar e instalar manualmente"
        echo "   1. Visita: https://ollama.com/download"
        echo "   2. Descarga el instalador para Linux"
        echo "   3. Ejecuta: bash <archivo_descargado>"
        echo ""
        echo "   Opción 2: Usar el método alternativo"
        echo "   curl -L https://ollama.com/download/ollama-linux-amd64 -o /tmp/ollama"
        echo "   chmod +x /tmp/ollama"
        echo "   sudo mv /tmp/ollama /usr/local/bin/ollama"
        echo ""
        echo "   Opción 3: Si ya tienes Ollama instalado en otro lugar"
        echo "   Asegúrate de que esté en tu PATH"
        echo ""
        read -p "   ¿Quieres intentar la instalación manual ahora? (s/n): " intentar_manual
        
        if [ "$intentar_manual" = "s" ]; then
            echo ""
            echo "   Descargando Ollama manualmente..."
            if curl --connect-timeout 30 --max-time 300 -L https://ollama.com/download/ollama-linux-amd64 -o /tmp/ollama 2>/dev/null; then
                chmod +x /tmp/ollama
                sudo mv /tmp/ollama /usr/local/bin/ollama 2>/dev/null
                if command -v ollama &> /dev/null; then
                    echo "✅ Ollama instalado manualmente"
                else
                    echo "❌ Error moviendo Ollama a /usr/local/bin"
                    echo "   Intenta ejecutar: sudo mv /tmp/ollama /usr/local/bin/ollama"
                    exit 1
                fi
            else
                echo "❌ Error descargando Ollama manualmente"
                echo "   Por favor instálalo manualmente desde: https://ollama.com"
                exit 1
            fi
        else
            echo ""
            echo "   Por favor instala Ollama manualmente antes de continuar"
            exit 1
        fi
    fi
else
    echo "✅ Ollama está instalado ($(ollama --version 2>/dev/null || echo 'versión desconocida'))"
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

# Verificar si los modelos están descargados (SIN restricciones)
echo ""
echo "🔍 Verificando modelos (sin restricciones de seguridad)..."
echo "   Modelos seleccionados:"
echo "   - Principal: $LLAMA_MODEL (sin restricciones)"
echo "   - Código: $DEEPSEEK_MODEL (sin restricciones)"
echo ""
MODELS=$(ollama list 2>/dev/null | grep -E "$LLAMA_MODEL|$DEEPSEEK_MODEL" || echo "")

if ! echo "$MODELS" | grep -q "$LLAMA_MODEL"; then
    echo "📥 Descargando modelo principal: $LLAMA_MODEL"
    echo "   Esto puede tomar varios minutos la primera vez..."
    ollama pull "$LLAMA_MODEL"
    if [ $? -ne 0 ]; then
        echo "⚠️  Error descargando modelo principal"
        echo "   Intentando modelo alternativo: mistral:7b"
        LLAMA_MODEL="mistral:7b"
        ollama pull "$LLAMA_MODEL" || {
            echo "❌ Error descargando modelo alternativo"
            echo "   Intenta manualmente: ollama pull mistral:7b"
        }
    else
        echo "✅ Modelo principal descargado"
    fi
else
    echo "✅ Modelo principal ya está disponible"
fi

if ! echo "$MODELS" | grep -q "$DEEPSEEK_MODEL"; then
    echo "📥 Descargando modelo de código: $DEEPSEEK_MODEL"
    echo "   Esto puede tomar varios minutos la primera vez..."
    ollama pull "$DEEPSEEK_MODEL"
    if [ $? -ne 0 ]; then
        echo "⚠️  Error descargando modelo de código"
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
