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

# ============================================================================
# CONFIGURACIÓN DE MODELOS - MEJORES MODELOS SIN RESTRICCIONES
# ============================================================================
# 
# Este proyecto está diseñado para usar los MEJORES modelos disponibles
# sin restricciones, optimizados para máximo rendimiento.
#
# CONSUMO DE RAM POR MODELO:
#
# MODELOS 7B (~4-6GB RAM cada uno):
#   1. mistral:7b          - ~4GB RAM  | Muy permisivo, excelente rendimiento
#   2. qwen2:7b            - ~4GB RAM  | Modelo chino, muy permisivo
#   3. llama2:7b           - ~4GB RAM  | Llama 2 sin restricciones de Llama 3
#   4. codellama:7b        - ~4GB RAM  | Enfocado en código, menos restrictivo
#
# MODELOS 13B+ (~12-20GB RAM cada uno) - MÁXIMO RENDIMIENTO:
#   5. mixtral:8x7b        - ~12GB RAM | ⭐ MEJOR MODELO GENERAL (8 expertos)
#   6. qwen2:14b           - ~14GB RAM | Modelo chino más grande, excelente
#   7. llama2:13b          - ~16GB RAM | Llama 2 más grande, muy potente
#   8. codellama:13b       - ~16GB RAM | ⭐ MEJOR MODELO PARA CÓDIGO
#   9. mistral-nemo:12b    - ~12GB RAM | Versión más grande de Mistral
#
# MODELOS PEQUEÑOS (~1-2GB RAM):
#   10. phi3:mini          - ~2GB RAM  | Pequeño pero permisivo
#   11. llama3.2:1b        - ~1GB RAM  | Muy ligero
#
# ============================================================================
# CONFIGURACIÓN POR DEFECTO - MEJORES MODELOS DISPONIBLES
# ============================================================================
# 
# Se usan los MEJORES modelos sin restricciones disponibles:
# - Modelo General: Mixtral 8x7B (8 expertos, máximo rendimiento)
# - Modelo Código: CodeLlama 13B (mejor para generación de código)
#
# RAM TOTAL NECESARIA: ~28GB (se cargan uno a la vez, máximo ~16GB simultáneo)
# RAM MÍNIMA RECOMENDADA: 32GB para uso cómodo
# RAM MÍNIMA ABSOLUTA: 20GB (con modelos 13B)
#
# Si tienes menos RAM, cambia a modelos 7B (ver opciones abajo)
# ============================================================================

# MEJORES MODELOS SIN RESTRICCIONES
# NOTA: Si tienes menos de 32GB RAM, usa modelos 7B (cambia las líneas de abajo)
# LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'mixtral:8x7b')  # ⭐ Mixtral 8x7B - MEJOR modelo general (~12GB RAM, pero necesita ~25GB total)
# DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'codellama:13b')  # ⭐ CodeLlama 13B - MEJOR para código (~16GB RAM)

# Modelos 7B (balance perfecto para sistemas con 16GB RAM)
LLAMA_MODEL = os.getenv('LLAMA_MODEL', 'mistral:7b')  # ~4GB RAM - Muy permisivo y sin restricciones
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'codellama:7b')  # ~4GB RAM - Excelente para código

# ALTERNATIVAS si tienes menos RAM:
# Opción 1: Modelos 7B (balance perfecto, ~8GB RAM total)
# LLAMA_MODEL = 'mistral:7b'  # ~4GB RAM
# DEEPSEEK_MODEL = 'codellama:7b'  # ~4GB RAM

# Opción 2: Modelos 13B individuales (máximo rendimiento, ~16-20GB RAM)
# LLAMA_MODEL = 'llama2:13b'  # ~16GB RAM
# DEEPSEEK_MODEL = 'codellama:13b'  # ~16GB RAM

# Configuración del servidor Flask
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
