"""
Configuración de la aplicación
"""
import os

# Configuración de la base de datos
DB_PATH = os.getenv('DB_PATH', 'chat.db')

# Configuración de Ollama (más estable que vLLM)
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
OLLAMA_CHAT_URL = os.getenv('OLLAMA_CHAT_URL', 'http://localhost:11434/api/chat')
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'llama3.2')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-coder')

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
