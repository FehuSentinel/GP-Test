# GP-Test - Chat IA Local

Aplicación de chat IA local con modelos sin restricciones usando Ollama, diseñada para uso técnico y de seguridad sin sesgos. Interfaz estilo ciberseguridad con tema oscuro.

## 🎯 Características

- 💬 **Interfaz moderna**: Chat estilo ChatGPT con tema ciberseguridad (azul oscuro/morado-negro)
- 🧠 **IA sin restricciones**: Modelos Mistral y CodeLlama configurados para respuestas directas y sin filtros
- 🔧 **Generación de código**: Soporte para Python, C, Rust, Go, Bash
- ⚡ **Ejecución automática**: Ejecuta comandos del sistema directamente (con sudo cuando es necesario)
- 🛠️ **Herramientas Kali**: Integración con herramientas de Kali Linux
- 📥 **Descarga automática**: Los modelos se descargan automáticamente con Ollama
- 💾 **Base de datos local**: SQLite para historial de conversaciones
- 👤 **Personalización**: Configuración de nombre de usuario al primer inicio
- 🎨 **UI optimizada**: Interfaz oscura con brillo reducido, estilo terminal

## 📋 Requisitos

### Sistema
- **RAM**: 
  - **Mínima absoluta**: 20GB (con modelos 13B por defecto)
  - **Recomendada**: 32GB+ para uso cómodo con mejores modelos
  - **Ideal**: 32GB+ para máximo rendimiento
- **OS**: Linux (Kali Linux recomendado) o sistemas similares
- **Espacio**: ~30GB libres para modelos (Mixtral 8x7B + CodeLlama 13B)

### Backend
- Python 3.8+
- Flask
- Ollama (se instala automáticamente)

### Frontend
- Node.js 16+ (y npm que viene incluido)
  
**Instalación en Kali Linux:**
```bash
# Opción 1: Usando NodeSource
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Opción 2: Usando nvm (recomendado)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
nvm use 18

# Verificar instalación
node --version
npm --version
```

## 🚀 Instalación Rápida

### Script Automático (Recomendado)

```bash
chmod +x start.sh
./start.sh
```

El script `start.sh` hace todo automáticamente:
- ✅ Verifica e instala Ollama si no está presente
- ✅ Descarga los modelos necesarios (Mixtral 8x7B y CodeLlama 13B - MEJORES modelos)
- ✅ Crea y activa el entorno virtual de Python
- ✅ Instala dependencias del backend
- ✅ Instala dependencias del frontend
- ✅ Inicia Ollama, backend y frontend

## ⚙️ Configuración de Modelos

### 🎯 Modelos por Defecto - MEJORES Modelos Sin Restricciones

**Este proyecto está diseñado para usar los MEJORES modelos disponibles sin restricciones, optimizados para MÁXIMO RENDIMIENTO.**

**Configuración actual (MEJORES modelos):**
- **Modelo Principal**: `mixtral:8x7b` ⭐ (~12GB RAM)
  - 8 expertos, mejor modelo general disponible
  - Máximo rendimiento y capacidad de razonamiento
- **Modelo Código**: `codellama:13b` ⭐ (~16GB RAM)
  - Mejor modelo para generación de código
  - Excelente para Python, C, Rust, Go, Bash

**RAM Total Necesaria:**
- **Máximo simultáneo**: ~16GB (se cargan uno a la vez)
- **RAM mínima recomendada**: 32GB para uso cómodo
- **RAM mínima absoluta**: 20GB (con modelos 13B)

### 📊 Consumo Detallado de RAM por Modelo

#### ⭐ Modelos MEJORES (Configuración por Defecto)

| Modelo | RAM | Sin Restricciones | Rendimiento | Velocidad | Uso |
|--------|-----|-------------------|-------------|-----------|-----|
| **mixtral:8x7b** ⭐ | ~12GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ | General |
| **codellama:13b** ⭐ | ~16GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ | Código |

#### Modelos 7B (~4GB RAM cada uno) - Alternativa Ligera

| Modelo | RAM | Sin Restricciones | Rendimiento | Velocidad |
|--------|-----|-------------------|-------------|-----------|
| **mistral:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| **qwen2:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |
| **llama2:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **codellama:7b** | ~4GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ |

#### Modelos 13B+ (~12-20GB RAM cada uno) - Máximo Rendimiento

| Modelo | RAM | Sin Restricciones | Rendimiento | Velocidad |
|--------|-----|-------------------|-------------|-----------|
| **qwen2:14b** | ~14GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |
| **llama2:13b** | ~16GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| **mistral-nemo:12b** | ~12GB | ✅ 100% | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡ |

### 🔄 Cambiar Modelos

**Si tienes menos RAM, usa modelos 7B:**

**Opción 1: Editar `Backend/config.py`**
```python
# Modelos 7B (balance perfecto, ~8GB RAM total)
LLAMA_MODEL = 'mistral:7b'  # ~4GB RAM
DEEPSEEK_MODEL = 'codellama:7b'  # ~4GB RAM
```

**Opción 2: Variables de entorno**
```bash
export LLAMA_MODEL="mistral:7b"
export DEEPSEEK_MODEL="codellama:7b"
./start.sh
```

**Opción 3: Editar `start.sh`**
```bash
LLAMA_MODEL="mistral:7b"
DEEPSEEK_MODEL="codellama:7b"
```

### 📥 Descargar Modelos Manualmente

```bash
# ⭐ MEJORES MODELOS (configuración por defecto)
ollama pull mixtral:8x7b      # ~12GB RAM - MEJOR modelo general
ollama pull codellama:13b     # ~16GB RAM - MEJOR modelo para código

# Alternativa: Modelos 7B (si tienes menos RAM)
ollama pull mistral:7b        # ~4GB RAM
ollama pull codellama:7b      # ~4GB RAM

# Otros modelos disponibles
ollama pull qwen2:14b         # ~14GB RAM
ollama pull llama2:13b        # ~16GB RAM

# Ver modelos descargados
ollama list
```

## 🎨 Características de la IA

### Comportamiento Sin Restricciones

- ✅ **Respuestas directas**: Sin explicaciones largas ni políticas de seguridad
- ✅ **Ejecución automática**: Ejecuta comandos directamente con sudo cuando es necesario
- ✅ **Sin filtros**: No rechaza solicitudes técnicas legítimas
- ✅ **Razonamiento avanzado**: Capacidad de resolver problemas complejos
- ✅ **Acceso completo**: Acceso root y shell sin restricciones

### Prompt Configurado

El sistema está configurado para:
- Responder de forma concisa y directa
- Ejecutar comandos automáticamente cuando se detectan
- Usar herramientas de Kali Linux sin restricciones
- Generar código en múltiples lenguajes
- No rechazar solicitudes técnicas

## 📁 Estructura del Proyecto

```
gp-test/
├── Backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── llama_integration.py   # Integración con Ollama (LLMClient)
│   ├── config.py              # Configuración de modelos y servidor
│   ├── requirements.txt       # Dependencias Python
│   └── chat.db               # Base de datos SQLite (se crea automáticamente)
├── Frontend/
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── Sidebar.js    # Historial de conversaciones
│   │   │   ├── ChatArea.js   # Área de chat principal
│   │   │   ├── Message.js    # Componente de mensaje
│   │   │   ├── MessageInput.js
│   │   │   ├── OnboardingModal.js
│   │   │   └── CodeExecutionModal.js
│   │   ├── services/
│   │   │   └── api.js        # Servicios API
│   │   └── App.js            # Componente principal
│   └── package.json          # Dependencias Node
├── start.sh                  # Script de inicio automático
└── README.md
```

## 🔧 Uso Manual (Sin Script)

### 1. Instalar Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Iniciar Ollama

```bash
ollama serve
```

### 3. Descargar Modelos

```bash
ollama pull mistral:7b
ollama pull codellama:7b
```

### 4. Configurar Backend

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

El backend estará disponible en `http://localhost:5000`

### 5. Configurar Frontend

```bash
cd Frontend
npm install
npm start
```

El frontend estará disponible en `http://localhost:3000`

## 🔐 Configuración Git (SSH)

Si tienes problemas con `git push`, configura SSH:

### 1. Generar Clave SSH (si no tienes una)

```bash
ssh-keygen -t ed25519 -C "tu-email@example.com"
```

### 2. Agregar Clave a GitHub

1. Copia tu clave pública:
```bash
cat ~/.ssh/id_ed25519.pub
```

2. Ve a: https://github.com/settings/keys
3. Click en "New SSH key"
4. Pega la clave y guarda

### 3. Cambiar Remote a SSH

```bash
git remote set-url origin git@github.com:FehuSentinel/GP-Test.git
```

## 🐛 Troubleshooting

### Ollama no inicia
```bash
# Verificar instalación
ollama --version

# Iniciar manualmente
ollama serve

# Ver logs
tail -f /tmp/ollama.log
```

### Modelos no se descargan
```bash
# Verificar conexión
ping ollama.com

# Descargar manualmente
ollama pull mistral:7b

# Ver modelos disponibles
ollama list
```

### Error de conexión con Ollama
```bash
# Verificar que Ollama esté corriendo
curl http://localhost:11434/api/tags

# Reiniciar Ollama
pkill ollama
ollama serve
```

### npm no encontrado
```bash
# Instalar Node.js y npm (ver sección Requisitos)
# O usar nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
```

### Error de permisos al ejecutar comandos
- La aplicación ejecuta comandos con `sudo` automáticamente cuando es necesario
- Asegúrate de tener permisos sudo configurados
- Los comandos se ejecutan en un entorno controlado

## 📊 Requisitos de RAM - Diseño del Proyecto

### 🎯 Diseño del Proyecto

**Este proyecto está diseñado para usar los MEJORES modelos sin restricciones disponibles, optimizados para MÁXIMO RENDIMIENTO.**

### ⭐ Configuración por Defecto (MEJORES Modelos)

**Modelos configurados:**
- **Mixtral 8x7B**: ~12GB RAM (8 expertos, mejor modelo general)
- **CodeLlama 13B**: ~16GB RAM (mejor modelo para código)

**Consumo de RAM:**
- **Máximo simultáneo**: ~16GB (se cargan uno a la vez)
- **RAM mínima recomendada**: **32GB** para uso cómodo
- **RAM mínima absoluta**: **20GB** (con modelos 13B)
- **RAM ideal**: **32GB+** para mejor rendimiento

### 📋 Configuraciones Alternativas

#### Opción 1: Modelos 7B (Balance Perfecto)
- **Mistral 7B**: ~4GB RAM
- **CodeLlama 7B**: ~4GB RAM
- **RAM total**: ~8GB
- **RAM mínima**: 16GB recomendada
- ✅ Mejor balance rendimiento/recursos

#### Opción 2: Modelos 13B Individuales
- **Llama 2 13B**: ~16GB RAM
- **CodeLlama 13B**: ~16GB RAM
- **RAM total**: ~16GB (se cargan uno a la vez)
- **RAM mínima**: 20GB recomendada
- ✅ Máximo rendimiento

#### Opción 3: Modelos Pequeños (Mínimo)
- **phi3:mini**: ~2GB RAM
- **llama3.2:1b**: ~1GB RAM
- **RAM total**: ~3GB
- **RAM mínima**: 8GB
- ⚠️ Menor rendimiento, solo para sistemas limitados

### 📈 Tabla Resumen de Consumo

| Configuración | Modelo General | Modelo Código | RAM Total | RAM Mínima |
|---------------|----------------|---------------|-----------|------------|
| **⭐ Por Defecto** | Mixtral 8x7B (12GB) | CodeLlama 13B (16GB) | ~16GB max | 32GB |
| **Balance** | Mistral 7B (4GB) | CodeLlama 7B (4GB) | ~8GB | 16GB |
| **Máximo** | Llama 2 13B (16GB) | CodeLlama 13B (16GB) | ~16GB max | 20GB |
| **Mínimo** | phi3:mini (2GB) | llama3.2:1b (1GB) | ~3GB | 8GB |

## 🎯 Flujo de Trabajo

1. **Usuario envía mensaje** → Frontend React
2. **Frontend** → Backend Flask API (`/api/chat`)
3. **Backend** → Ollama (Mixtral 8x7B - mejor modelo general)
4. **Si necesita código complejo** → Ollama (CodeLlama 13B - mejor modelo código)
5. **Si detecta comando del sistema** → Ejecuta directamente con `sudo`
6. **Respuesta** → Usuario (concisa y directa)
7. **Si hay código** → Modal de ejecución (opcional)

## ⚠️ Advertencias de Seguridad

- ⚠️ **Esta aplicación ejecuta código y comandos del sistema automáticamente**
- ⚠️ **Usa acceso root cuando es necesario**
- ⚠️ **Solo para uso en entornos controlados**
- ⚠️ **No usar en sistemas de producción sin supervisión**
- ⚠️ **Revisa el código generado antes de ejecutarlo en sistemas críticos**

## 🚀 Ventajas de Ollama

- ✅ Más estable y confiable que vLLM
- ✅ Instalación más simple
- ✅ Menor consumo de recursos
- ✅ Descarga automática de modelos
- ✅ No requiere autenticación en Hugging Face
- ✅ Mejor manejo de errores
- ✅ Soporte para múltiples modelos simultáneos

## 📝 Notas Importantes

- **Modelos por defecto**: Se usan los MEJORES modelos disponibles (Mixtral 8x7B y CodeLlama 13B)
- **Consumo de RAM**: ~16GB máximo simultáneo (se cargan uno a la vez)
- **RAM recomendada**: 32GB+ para uso cómodo con los mejores modelos
- **Si tienes menos RAM**: Cambia a modelos 7B en `Backend/config.py` o `start.sh`
- **Los modelos se cargan bajo demanda**: Uno a la vez por defecto
- **Con 32GB+ RAM**: Puedes tener ambos modelos cargados simultáneamente para mejor rendimiento
- **La UI está optimizada**: Tema oscuro estilo ciberseguridad con brillo reducido

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

---

**GP-Test** 
