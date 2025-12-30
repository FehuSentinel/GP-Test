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

# Modelos recomendados SIN restricciones (optimizado para 25GB RAM):
# 
# MODELOS 7B (~4GB RAM cada uno):
# 1. mistral:7b - Muy permisivo, excelente rendimiento
# 2. qwen2:7b - Modelo chino, muy permisivo
# 3. llama2:7b - Llama 2 sin restricciones de Llama 3
# 4. codellama:7b - Enfocado en código, menos restrictivo
#
# MODELOS 13B (~16-20GB RAM cada uno) - RECOMENDADO para 25GB RAM:
# 5. mistral-nemo:12b - Versión más grande de Mistral (~12GB RAM)
# 6. qwen2:14b - Modelo chino más grande (~14GB RAM)
# 7. llama2:13b - Llama 2 más grande (~16GB RAM)
# 8. codellama:13b - CodeLlama más grande (~16GB RAM)
#
# MODELOS PEQUEÑOS (si necesitas ahorrar RAM):
# 9. phi3:mini - Pequeño pero permisivo (~2GB RAM)

# Configuración optimizada para 25GB RAM - Modelos más potentes
# Puedes cambiar a modelos 13B si quieres mejor rendimiento:
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'mistral:7b')  # Mistral 7B (muy permisivo)
# Para código, CodeLlama 7B o 13B si quieres más potencia
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'codellama:7b')  # CodeLlama 7B

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
