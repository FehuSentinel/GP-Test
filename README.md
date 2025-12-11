# GP-Test - Chat IA Local Sin Sesgo

Aplicación de chat IA local con Llama y DeepSeek usando Ollama, diseñada para uso técnico y de seguridad sin sesgos.

## Características

- 💬 Interfaz de chat moderna estilo ChatGPT
- 🧠 Integración con Llama local (vía Ollama - más estable)
- 🤖 Integración con DeepSeek local (vía Ollama) para generación de código
- 🔧 Generación y ejecución de scripts (Python, C, Rust, Go, Bash)
- 📥 Descarga automática de modelos con Ollama
- 💾 Base de datos SQLite local
- 🎯 Prompt sin sesgo configurado
- 👤 Personalización con nombre de usuario
- 🛠️ Uso de herramientas de Kali Linux

## Requisitos

### Backend
- Python 3.8+
- Flask
- Ollama instalado (el script lo instala automáticamente)

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

### Opción 1: Script automático (Recomendado)

```bash
./start.sh
```

El script:
- Instala Ollama automáticamente si no está instalado
- Descarga los modelos necesarios (Llama y DeepSeek)
- Configura el backend y frontend
- Inicia todos los servicios

### Opción 2: Manual

#### 1. Instalar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 2. Iniciar Ollama

```bash
ollama serve
```

#### 3. Descargar modelos

```bash
ollama pull llama3.2
ollama pull deepseek-coder
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

Los modelos se descargan automáticamente con Ollama. Los modelos por defecto son:

- **Llama**: `llama3.2`
- **DeepSeek**: `deepseek-coder`

Puedes cambiarlos en `Backend/config.py` o mediante variables de entorno.

Para ver modelos disponibles:
```bash
ollama list
```

Para descargar otros modelos:
```bash
ollama pull nombre-del-modelo
```

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
- Instala Ollama automáticamente si no está instalado
- Descarga los modelos necesarios
- Configura backend y frontend
- Inicia todos los servicios

### Opción 2: Manual

#### 1. Iniciar Ollama

```bash
ollama serve
```

#### 2. Iniciar Backend

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
│   ├── llama_integration.py   # Integración con Llama/DeepSeek vía Ollama
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
3. Backend → Llama (vía Ollama)
4. Si Llama necesita código complejo → DeepSeek (vía Ollama)
5. Respuesta → Usuario
6. Si hay código → Usuario decide si ejecutarlo

## Ventajas de Ollama sobre vLLM

- ✅ Más estable y confiable
- ✅ Instalación más simple
- ✅ Menor consumo de recursos
- ✅ Descarga automática de modelos
- ✅ No requiere autenticación en Hugging Face
- ✅ Mejor manejo de errores

## Notas de Seguridad

⚠️ **ADVERTENCIA**: Esta aplicación puede ejecutar código y comandos del sistema. Úsala con precaución y solo en entornos controlados.

## Troubleshooting

### Ollama no inicia
- Verifica que Ollama esté instalado: `ollama --version`
- Inicia el servicio manualmente: `ollama serve`
- Verifica los logs: `tail -f /tmp/ollama.log`

### Modelos no se descargan
- Verifica tu conexión a internet
- Intenta descargar manualmente: `ollama pull llama3.2`
- Verifica modelos disponibles: `ollama list`

### Error de conexión
- Verifica que Ollama esté corriendo: `curl http://localhost:11434/api/tags`
- Reinicia Ollama: `pkill ollama && ollama serve`

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.
