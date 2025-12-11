# Modelos Sin Restricciones de Seguridad

## Modelos Recomendados (de menos a más restrictivo)

### 1. Mistral 7B ⭐ RECOMENDADO
```bash
ollama pull mistral:7b
```
- **Ventajas:** Muy permisivo, excelente rendimiento, menos restricciones
- **RAM:** ~4GB
- **Uso:** `LLAMA_MODEL="mistral:7b"`

### 2. Qwen2 7B
```bash
ollama pull qwen2:7b
```
- **Ventajas:** Modelo chino, muy permisivo, buen rendimiento
- **RAM:** ~4GB
- **Uso:** `LLAMA_MODEL="qwen2:7b"`

### 3. Llama 2 7B
```bash
ollama pull llama2:7b
```
- **Ventajas:** Llama 2 sin las restricciones de Llama 3
- **RAM:** ~4GB
- **Uso:** `LLAMA_MODEL="llama2:7b"`

### 4. CodeLlama 7B
```bash
ollama pull codellama:7b
```
- **Ventajas:** Enfocado en código, menos restrictivo
- **RAM:** ~4GB
- **Uso:** `DEEPSEEK_MODEL="codellama:7b"`

### 5. Phi-3 Mini
```bash
ollama pull phi3:mini
```
- **Ventajas:** Pequeño pero permisivo, menos recursos
- **RAM:** ~2GB
- **Uso:** `LLAMA_MODEL="phi3:mini"`

## Modelos con Restricciones (evitar)

- ❌ `llama3.2` - Tiene restricciones de seguridad incorporadas
- ❌ `llama3.1` - Tiene restricciones de seguridad incorporadas
- ❌ `deepseek-coder` - Puede tener algunas restricciones

## Configuración

### Opción 1: Variables de entorno
```bash
export LLAMA_MODEL="mistral:7b"
export DEEPSEEK_MODEL="codellama:7b"
./start.sh
```

### Opción 2: Editar config.py
Edita `Backend/config.py`:
```python
LLAMA_MODEL = 'mistral:7b'
DEEPSEEK_MODEL = 'codellama:7b'
```

### Opción 3: Editar start.sh
Edita `start.sh`:
```bash
LLAMA_MODEL="mistral:7b"
DEEPSEEK_MODEL="codellama:7b"
```

## Verificar Modelos Disponibles
```bash
ollama list
```

## Descargar Modelo Específico
```bash
ollama pull nombre-del-modelo
```

## Notas

- Los modelos sin restricciones son más permisivos pero requieren más responsabilidad
- Mistral 7B es la mejor opción balance entre permisos y rendimiento
- CodeLlama es excelente para generación de código sin restricciones
- Si tienes pocos recursos, usa Phi-3 Mini

