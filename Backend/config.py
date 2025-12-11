"""
Configuración de la aplicación
"""
import os

# Configuración de la base de datos
DB_PATH = os.getenv('DB_PATH', 'chat.db')

# Configuración de Ollama (más estable que vLLM)
# Modelos SIN restricciones de seguridad - más permisivos
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/generate')
OLLAMA_CHAT_URL = os.getenv('OLLAMA_CHAT_URL', 'http://localhost:11434/api/chat')

# Modelos recomendados SIN restricciones (de menos a más restrictivo):
# 1. mistral:7b - Muy permisivo, buen rendimiento (~4GB RAM)
# 2. qwen2:7b - Modelo chino, muy permisivo (~4GB RAM)
# 3. llama2:7b - Llama 2 sin restricciones de Llama 3 (~4GB RAM)
# 4. codellama:7b - Enfocado en código, menos restrictivo (~4GB RAM)
# 5. phi3:mini - Pequeño pero permisivo (~2GB RAM)
# 6. llama3.2:1b - Llama 3.2 (tiene restricciones pero pequeño)

# Modelos ligeros SIN restricciones por defecto
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'mistral:7b')  # Cambiado a Mistral (menos restrictivo)
# Para código, usar codellama o deepseek-coder
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'codellama:7b')  # CodeLlama menos restrictivo

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
