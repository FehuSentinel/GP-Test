# Modelos Ligeros para GP-Test

## Modelos Recomendados por Recursos Disponibles

### Muy Poco RAM (< 2GB disponible)
```bash
# Modelos ultra ligeros
ollama pull phi3:mini          # ~2GB RAM, muy rápido
ollama pull tinyllama          # ~600MB RAM, básico pero funcional
```

### Poco RAM (2-4GB disponible)
```bash
# Modelos ligeros recomendados
ollama pull llama3.2:1b        # ~600MB RAM, buena calidad
ollama pull deepseek-coder:1.3b # ~800MB RAM, bueno para código
```

### RAM Moderada (4-8GB disponible)
```bash
# Modelos balanceados
ollama pull llama3.2:3b        # ~2GB RAM, mejor calidad
ollama pull codellama:7b-code  # ~4GB RAM, excelente para código
```

### RAM Suficiente (8GB+ disponible)
```bash
# Modelos completos (mejor calidad)
ollama pull llama3.2          # ~4GB RAM, alta calidad
ollama pull deepseek-coder     # ~4GB RAM, excelente para código
```

## Configurar Modelos en GP-Test

### Opción 1: Variables de entorno
```bash
export LLAMA_MODEL="llama3.2:1b"
export DEEPSEEK_MODEL="deepseek-coder:1.3b"
./start.sh
```

### Opción 2: Editar config.py
Edita `Backend/config.py` y cambia:
```python
LLAMA_MODEL = 'llama3.2:1b'
DEEPSEEK_MODEL = 'deepseek-coder:1.3b'
```

## Optimización de Recursos

### Reducir consumo de CPU
En `Backend/llama_integration.py`, los modelos ya están configurados con:
- `num_thread: 2` - Menos threads de CPU
- `num_ctx: 2048` - Contexto reducido
- `num_predict: 1000` - Respuestas más cortas

### Variables de entorno de Ollama
```bash
export OLLAMA_NUM_PARALLEL=1      # Solo una solicitud a la vez
export OLLAMA_MAX_LOADED_MODELS=1 # Solo un modelo en memoria
export OLLAMA_NUM_GPU=0          # Sin GPU (solo CPU)
```

## Verificar Modelos Disponibles
```bash
ollama list
```

## Descargar Modelo Específico
```bash
ollama pull nombre-del-modelo
```

