"""
Configuración de la aplicación
"""
import os

# Configuración de la base de datos
DB_PATH = os.getenv('DB_PATH', 'chat.db')

# Configuración de vLLM
VLLM_API_URL = os.getenv('VLLM_API_URL', 'http://localhost:8000/v1/chat/completions')
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'meta-llama/Llama-3.1-8B-Instruct')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-ai/deepseek-coder-6.7b-instruct')

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

