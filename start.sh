#!/bin/bash

# Script para iniciar la aplicación completa con Ollama

echo "=== GP-Test - Iniciando aplicación ==="
echo ""

# Verificar e instalar Ollama
OLLAMA_PID=""

# ============================================================================
# CONFIGURACIÓN DE MODELOS - MEJORES MODELOS SIN RESTRICCIONES
# ============================================================================
# 
# Este proyecto usa los MEJORES modelos disponibles sin restricciones.
# Configurados para MÁXIMO RENDIMIENTO, independiente de RAM.
#
# CONSUMO DE RAM:
#   - Mixtral 8x7B: ~12GB RAM (8 expertos, mejor modelo general)
#   - CodeLlama 13B: ~16GB RAM (mejor modelo para código)
#   - RAM TOTAL: ~28GB (se cargan uno a la vez, máximo ~16GB simultáneo)
#
# RAM MÍNIMA RECOMENDADA: 32GB para uso cómodo
# RAM MÍNIMA ABSOLUTA: 20GB (con modelos 13B)
#
# Si tienes menos RAM, cambia a modelos 7B (ver opciones abajo)
# ============================================================================

# ⭐ MEJORES MODELOS SIN RESTRICCIONES (MÁXIMO RENDIMIENTO)
# NOTA: Si tienes menos de 32GB RAM, usa modelos 7B (descomenta las líneas de abajo)
# LLAMA_MODEL="mixtral:8x7b"      # ⭐ MEJOR modelo general - 8 expertos (~12GB RAM, pero necesita ~25GB total)
# DEEPSEEK_MODEL="codellama:13b"  # ⭐ MEJOR modelo para código (~16GB RAM)

# Modelos 7B (balance perfecto para sistemas con 16GB RAM)
LLAMA_MODEL="mistral:7b"       # ~4GB RAM - Muy permisivo y sin restricciones
DEEPSEEK_MODEL="codellama:7b"  # ~4GB RAM - Excelente para código

# ALTERNATIVAS si tienes menos RAM:
# Opción 1: Modelos 7B (balance perfecto, ~8GB RAM total)
# LLAMA_MODEL="mistral:7b"       # ~4GB RAM
# DEEPSEEK_MODEL="codellama:7b"  # ~4GB RAM

# Opción 2: Modelos 13B individuales (máximo rendimiento, ~16-20GB RAM)
# LLAMA_MODEL="llama2:13b"       # ~16GB RAM
# DEEPSEEK_MODEL="codellama:13b" # ~16GB RAM

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
echo "⏳ IMPORTANTE: Los modelos se descargarán completamente antes de iniciar la aplicación."
echo "   Esto puede tardar varios minutos dependiendo de tu conexión."
echo ""

# Función para verificar si un modelo está realmente disponible
check_model_available() {
    local model_name=$1
    ollama list 2>/dev/null | grep -q "^$model_name" || ollama list 2>/dev/null | grep -q "$model_name"
}

# Verificar y descargar modelo principal
MODELS=$(ollama list 2>/dev/null || echo "")

if ! check_model_available "$LLAMA_MODEL"; then
    echo "📥 Descargando modelo principal: $LLAMA_MODEL"
    echo "   ⏳ Esto puede tomar varios minutos (modelo grande)..."
    echo "   💡 Puedes ver el progreso arriba"
    echo ""
    
    if ollama pull "$LLAMA_MODEL"; then
        # Verificar que realmente se descargó
        if check_model_available "$LLAMA_MODEL"; then
            echo "✅ Modelo principal descargado y verificado: $LLAMA_MODEL"
        else
            echo "⚠️  Modelo descargado pero no aparece en la lista. Verificando..."
            sleep 2
            if check_model_available "$LLAMA_MODEL"; then
                echo "✅ Modelo principal verificado: $LLAMA_MODEL"
            else
                echo "❌ Error: Modelo no disponible después de descargar"
                echo "   Intenta manualmente: ollama pull $LLAMA_MODEL"
                exit 1
            fi
        fi
    else
        echo "❌ Error descargando modelo principal: $LLAMA_MODEL"
        echo "   Verifica tu conexión a internet y espacio en disco"
        exit 1
    fi
else
    echo "✅ Modelo principal ya está disponible: $LLAMA_MODEL"
fi

echo ""

# Verificar y descargar modelo de código
if ! check_model_available "$DEEPSEEK_MODEL"; then
    echo "📥 Descargando modelo de código: $DEEPSEEK_MODEL"
    echo "   ⏳ Esto puede tomar varios minutos (modelo grande)..."
    echo "   💡 Puedes ver el progreso arriba"
    echo ""
    
    if ollama pull "$DEEPSEEK_MODEL"; then
        # Verificar que realmente se descargó
        if check_model_available "$DEEPSEEK_MODEL"; then
            echo "✅ Modelo de código descargado y verificado: $DEEPSEEK_MODEL"
        else
            echo "⚠️  Modelo descargado pero no aparece en la lista. Verificando..."
            sleep 2
            if check_model_available "$DEEPSEEK_MODEL"; then
                echo "✅ Modelo de código verificado: $DEEPSEEK_MODEL"
            else
                echo "❌ Error: Modelo no disponible después de descargar"
                echo "   Intenta manualmente: ollama pull $DEEPSEEK_MODEL"
                exit 1
            fi
        fi
    else
        echo "❌ Error descargando modelo de código: $DEEPSEEK_MODEL"
        echo "   Verifica tu conexión a internet y espacio en disco"
        exit 1
    fi
else
    echo "✅ Modelo de código ya está disponible: $DEEPSEEK_MODEL"
fi

echo ""
echo "✅ Todos los modelos están listos. Continuando con la configuración..."
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
