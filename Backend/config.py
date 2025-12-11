"""
Configuración de la aplicación
"""
import os

# Configuración de la base de datos
DB_PATH = os.getenv('DB_PATH', 'chat.db')

# Configuración de Ollama (más estable que vLLM)
# Modelos optimizados para bajo consumo de recursos
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
OLLAMA_CHAT_URL = os.getenv('OLLAMA_CHAT_URL', 'http://localhost:11434/api/chat')
# Modelos ligeros por defecto (puedes cambiarlos según tus recursos)
# Opciones: llama3.2:1b (~600MB RAM), llama3.2:3b (~2GB), llama3.2 (~4GB)
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'llama3.2:1b')
# Opciones: deepseek-coder:1.3b (~800MB RAM), deepseek-coder:6.7b (~4GB)
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-coder:1.3b')

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
