# Requisitos de RAM - Modelos Sin Restricciones

## 📊 Resumen de RAM Necesaria

### Configuración Actual (Recomendada)
- **Modelo Principal:** Mistral 7B → **~4GB RAM**
- **Modelo Código:** CodeLlama 7B → **~4GB RAM**
- **Total mínimo:** **~8GB RAM** (pero solo se carga uno a la vez)
- **RAM real necesaria:** **~5-6GB** (con margen para el sistema)

### ⚠️ IMPORTANTE
Los modelos se cargan **uno a la vez**, no simultáneamente. Entonces:
- Si usas solo Mistral 7B: **~4GB RAM**
- Si usas solo CodeLlama 7B: **~4GB RAM**
- Si alternas entre ambos: **~5-6GB RAM** (con margen)

---

## 🎯 Modelos 100% Sin Restricciones (de más a menos RAM)

### Opción 1: Máximo Rendimiento (Recomendado)
```
Modelo Principal: mistral:7b
Modelo Código: codellama:7b
RAM necesaria: ~5-6GB
```
✅ **Mejor balance entre permisos y rendimiento**

### Opción 2: Menos RAM pero Bueno
```
Modelo Principal: qwen2:7b
Modelo Código: codellama:7b
RAM necesaria: ~5-6GB
```
✅ **Muy permisivo, buen rendimiento**

### Opción 3: Mínimo RAM (Funcional)
```
Modelo Principal: phi3:mini
Modelo Código: phi3:mini (mismo modelo)
RAM necesaria: ~2-3GB
```
✅ **Funciona con poca RAM, permisivo**
⚠️ **Menos capacidad que los modelos 7B**

### Opción 4: Llama 2 (Sin restricciones de Llama 3)
```
Modelo Principal: llama2:7b
Modelo Código: codellama:7b
RAM necesaria: ~5-6GB
```
✅ **Llama 2 sin las restricciones de Llama 3**

---

## 📋 Tabla Comparativa

| Modelo | RAM | Sin Restricciones | Rendimiento | Recomendado |
|--------|-----|-------------------|-------------|-------------|
| **mistral:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⭐ SÍ |
| **qwen2:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ✅ SÍ |
| **llama2:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐ | ✅ SÍ |
| **codellama:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ✅ SÍ (código) |
| **phi3:mini** | ~2GB | ✅ 100% | ⭐⭐⭐ | ⚠️ Si tienes poca RAM |

---

## 🔧 Configuración Según tu RAM

### Si tienes ≥ 8GB RAM
```bash
# Usa la configuración actual (recomendada)
LLAMA_MODEL="mistral:7b"
DEEPSEEK_MODEL="codellama:7b"
```
**RAM necesaria:** ~5-6GB

### Si tienes 4-6GB RAM
```bash
# Usa modelos más pequeños
LLAMA_MODEL="phi3:mini"
DEEPSEEK_MODEL="phi3:mini"
```
**RAM necesaria:** ~2-3GB
⚠️ **Menos capacidad pero funciona**

### Si tienes < 4GB RAM
```bash
# Usa solo un modelo pequeño
LLAMA_MODEL="phi3:mini"
DEEPSEEK_MODEL="phi3:mini"
```
**RAM necesaria:** ~2GB
⚠️ **Puede ser lento, pero funciona**

---

## 💡 Optimizaciones para Reducir RAM

### 1. Usar solo un modelo
Si solo necesitas un modelo, configura ambos iguales:
```python
LLAMA_MODEL = 'mistral:7b'
DEEPSEEK_MODEL = 'mistral:7b'  # Mismo modelo
```

### 2. Variables de entorno de Ollama
En `start.sh` ya están configuradas:
```bash
export OLLAMA_NUM_PARALLEL=1        # Solo 1 solicitud a la vez
export OLLAMA_MAX_LOADED_MODELS=1   # Solo 1 modelo en memoria
export OLLAMA_NUM_GPU=0              # Usar CPU (ahorra VRAM)
```

### 3. Cerrar otros programas
- Cierra navegadores con muchas pestañas
- Cierra aplicaciones pesadas
- Libera RAM antes de iniciar

---

## 🚫 Modelos a EVITAR (tienen restricciones)

- ❌ `llama3.2` - Tiene restricciones de seguridad
- ❌ `llama3.1` - Tiene restricciones de seguridad
- ❌ `llama3` - Tiene restricciones de seguridad
- ⚠️ `deepseek-coder` - Puede tener algunas restricciones

---

## ✅ Recomendación Final

**Para 100% sin restricciones y buen rendimiento:**
- **Mistral 7B** + **CodeLlama 7B**
- **RAM necesaria:** ~5-6GB
- **Configuración:** Ya está en `config.py` y `start.sh`

**Si tienes poca RAM:**
- **Phi-3 Mini** (mismo para ambos)
- **RAM necesaria:** ~2-3GB
- **Cambia en:** `config.py` o `start.sh`

---

## 🔍 Verificar RAM Disponible

```bash
# Ver RAM total y disponible
free -h

# Ver RAM usada por procesos
htop

# Ver RAM usada por Ollama
ps aux | grep ollama
```

---

## 📝 Notas Importantes

1. **Los modelos se cargan bajo demanda** - Solo se carga el que se usa
2. **Ollama gestiona la memoria** - Libera modelos cuando no se usan
3. **El sistema operativo necesita RAM** - Deja ~2GB libres para el sistema
4. **Mejor tener margen** - Si tienes 8GB, usa modelos que necesiten ~5-6GB máximo

