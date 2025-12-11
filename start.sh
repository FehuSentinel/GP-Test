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
        cd Backend
        source venv/bin/activate 2>/dev/null || true
        python3 setup_models.py &
        VLLM_PID=$!
        cd ..
        echo "⏳ Esperando a que vLLM esté listo..."
        sleep 10
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
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    if [ ! -z "$VLLM_PID" ]; then
        kill $VLLM_PID 2>/dev/null
    fi
    exit
}
trap cleanup INT TERM
wait

