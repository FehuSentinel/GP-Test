# Chat IA Local - Sin Sesgo

Aplicación de chat IA local con Llama y DeepSeek usando vLLM, diseñada para uso técnico y de seguridad sin sesgos.

## Características

- 💬 Interfaz de chat moderna estilo ChatGPT
- 🧠 Integración con Llama local (vía vLLM)
- 🤖 Integración con DeepSeek local (vía vLLM) para generación de código
- 🔧 Generación y ejecución de scripts (Python, C, Rust, Go, Bash)
- 📥 Descarga automática de modelos si no están disponibles
- 💾 Base de datos SQLite local
- 🎯 Prompt sin sesgo configurado
- 👤 Personalización con nombre de usuario
- 🛠️ Uso de herramientas de Kali Linux

## Requisitos

### Backend
- Python 3.8+
- Flask
- vLLM instalado
- Cuenta de Hugging Face (para descargar modelos)

### Frontend
- Node.js 16+ (y npm que viene incluido)
  
  **Instalación en Kali Linux:**
  ```bash
  # Opción 1: Usando NodeSource
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs
  
  # Opción 2: Usando nvm (recomendado)
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
  source ~/.bashrc
  nvm install 18
  nvm use 18
  
  # Verificar instalación
  node --version
  npm --version
  ```

## Instalación

### 1. Instalar vLLM

```bash
pip install vllm
```

### 2. Autenticarse en Hugging Face

```bash
huggingface-cli login
```

### 3. Instalar dependencias del Backend

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Instalar dependencias del Frontend

```bash
cd Frontend
npm install
```

## Configuración

### Modelos

Los modelos se descargan automáticamente la primera vez que se usan. Los modelos por defecto son:

- **Llama**: `meta-llama/Llama-3.1-8B-Instruct`
- **DeepSeek**: `deepseek-ai/deepseek-coder-6.7b-instruct`

Puedes cambiarlos en `Backend/config.py` o mediante variables de entorno.

### Frontend

Crea un archivo `.env` en la carpeta Frontend (opcional):
```
REACT_APP_API_URL=http://localhost:5000/api
```

## Uso

### Opción 1: Script automático (Recomendado)

```bash
./start.sh
```

Este script:
- Verifica si vLLM está corriendo
- Instala dependencias automáticamente
- Inicia backend y frontend

### Opción 2: Manual

#### 1. Iniciar vLLM

```bash
# Con Llama (para chat general)
vllm serve meta-llama/Llama-3.1-8B-Instruct

# O con DeepSeek (para generación de código)
vllm serve deepseek-ai/deepseek-coder-6.7b-instruct
```

**Nota**: vLLM solo puede cargar un modelo a la vez. Para cambiar de modelo, detén vLLM e inícialo con el otro modelo.

#### 2. Verificar/Configurar modelos

```bash
cd Backend
python3 setup_models.py
```

#### 3. Iniciar Backend

```bash
cd Backend
source venv/bin/activate
python app.py
```

El backend estará disponible en `http://localhost:5000`

#### 4. Iniciar Frontend

```bash
cd Frontend
npm start
```

El frontend estará disponible en `http://localhost:3000`

## Estructura del Proyecto

```
gp-test/
├── Backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── llama_integration.py   # Integración con Llama/DeepSeek vía vLLM
│   ├── setup_models.py        # Script para verificar/descargar modelos
│   ├── config.py              # Configuración
│   ├── requirements.txt       # Dependencias Python
│   └── chat.db               # Base de datos SQLite (se crea automáticamente)
├── Frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── services/         # Servicios API
│   │   └── App.js            # Componente principal
│   └── package.json          # Dependencias Node
├── start.sh                  # Script de inicio automático
└── README.md
```

## Características Técnicas

- **Sin sesgo**: El prompt está configurado para ser objetivo y técnico
- **Ejecución segura**: Los scripts se muestran antes de ejecutarse
- **Historial persistente**: Todas las conversaciones se guardan en SQLite
- **Código generado**: Soporte para múltiples lenguajes de programación
- **Integración DeepSeek**: Llama puede solicitar código complejo a DeepSeek cuando sea necesario
- **100% Local**: Todo funciona localmente sin APIs externas

## Flujo de Trabajo

1. Usuario envía mensaje → Frontend
2. Frontend → Backend Flask API
3. Backend → Llama (vía vLLM)
4. Si Llama necesita código complejo → DeepSeek (vía vLLM)
5. Respuesta → Usuario
6. Si hay código → Usuario decide si ejecutarlo

## Notas de Seguridad

⚠️ **ADVERTENCIA**: Esta aplicación puede ejecutar código y comandos del sistema. Úsala con precaución y solo en entornos controlados.

## Troubleshooting

### vLLM no inicia
- Verifica que tengas suficiente RAM (recomendado: 16GB+)
- Asegúrate de estar autenticado en Hugging Face: `huggingface-cli login`
- Verifica que el modelo existe y tienes acceso

### Modelos no se descargan
- Verifica tu conexión a internet
- Asegúrate de estar autenticado en Hugging Face
- Algunos modelos requieren solicitar acceso en Hugging Face

### Error de conexión
- Verifica que vLLM esté corriendo en `http://localhost:8000`
- Verifica que el modelo esté cargado correctamente

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
