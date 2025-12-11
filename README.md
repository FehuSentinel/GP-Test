# Chat IA Local - Sin Sesgo

Aplicación de chat IA local con Llama3B, diseñada para uso técnico y de seguridad sin sesgos.

## Características

- 💬 Interfaz de chat moderna estilo ChatGPT
- 🧠 Integración con Llama3B local (vía Ollama)
- 🔧 Generación y ejecución de scripts (Python, C, Rust, Go, Bash)
- 🤖 Integración opcional con DeepSeek API para código complejo
- 💾 Base de datos SQLite local
- 🎯 Prompt sin sesgo configurado
- 👤 Personalización con nombre de usuario
- 🛠️ Uso de herramientas de Kali Linux

## Requisitos

### Backend
- Python 3.8+
- Flask
- Ollama con Llama3B instalado (o modelo compatible)

### Frontend
- Node.js 16+
- npm o yarn

### Opcional
- DeepSeek API Key (si se quiere usar generación de código avanzada)

## Instalación

### Backend

```bash
cd Backend
pip install -r requirements.txt
```

### Frontend

```bash
cd Frontend
npm install
```

## Configuración

### Backend

1. Asegúrate de tener Ollama corriendo con Llama3B:
```bash
ollama pull llama3.2
ollama serve
```

2. (Opcional) Configura DeepSeek API Key:
```bash
export DEEPSEEK_API_KEY=tu_api_key_aqui
```

### Frontend

Crea un archivo `.env` en la carpeta Frontend:
```
REACT_APP_API_URL=http://localhost:5000/api
```

## Uso

### Iniciar Backend

```bash
cd Backend
python app.py
```

El backend estará disponible en `http://localhost:5000`

### Iniciar Frontend

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
│   ├── llama_integration.py   # Integración con Llama3B
│   ├── deepseek_integration.py # Integración con DeepSeek
│   ├── requirements.txt       # Dependencias Python
│   └── chat.db               # Base de datos SQLite (se crea automáticamente)
├── Frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── services/         # Servicios API
│   │   └── App.js            # Componente principal
│   └── package.json          # Dependencias Node
└── README.md
```

## Características Técnicas

- **Sin sesgo**: El prompt está configurado para ser objetivo y técnico
- **Ejecución segura**: Los scripts se muestran antes de ejecutarse
- **Historial persistente**: Todas las conversaciones se guardan en SQLite
- **Código generado**: Soporte para múltiples lenguajes de programación
- **Integración DeepSeek**: Llama puede solicitar código complejo a DeepSeek cuando sea necesario

## Notas de Seguridad

⚠️ **ADVERTENCIA**: Esta aplicación puede ejecutar código y comandos del sistema. Úsala con precaución y solo en entornos controlados.

## Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

