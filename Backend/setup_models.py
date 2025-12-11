#!/usr/bin/env python3
"""
Script para verificar y descargar modelos automáticamente usando vLLM
"""
import subprocess
import sys
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Modelos a verificar/descargar
LLAMA_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
DEEPSEEK_MODEL = "deepseek-ai/deepseek-coder-6.7b-instruct"

VLLM_URL = "http://localhost:8000/v1/models"

def check_vllm_running():
    """Verifica si vLLM está corriendo"""
    try:
        response = requests.get(VLLM_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def check_model_loaded(model_name):
    """Verifica si un modelo está cargado en vLLM"""
    try:
        response = requests.get(VLLM_URL, timeout=5)
        if response.status_code == 200:
            models = response.json()
            loaded_models = models.get('data', [])
            return any(m.get('id') == model_name for m in loaded_models)
    except:
        pass
    return False

def start_vllm_with_model(model_name):
    """Inicia vLLM con un modelo específico"""
    logger.info(f"🚀 Iniciando vLLM con modelo: {model_name}")
    logger.info("   Esto puede tomar varios minutos la primera vez que descarga el modelo...")
    
    cmd = ["vllm", "serve", model_name]
    logger.info(f"   Ejecutando: {' '.join(cmd)}")
    
    # Iniciar vLLM en background
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Esperar a que vLLM esté listo
    logger.info("   Esperando a que vLLM esté listo...")
    for i in range(60):  # Esperar hasta 5 minutos
        time.sleep(5)
        if check_vllm_running():
            logger.info("   ✅ vLLM está corriendo!")
            return process
        logger.info(f"   Esperando... ({i+1}/60)")
    
    logger.error("   ⚠️ vLLM no respondió a tiempo")
    return None

def main():
    logger.info("=== Verificación de modelos vLLM ===")
    
    # Verificar si vLLM está corriendo
    if check_vllm_running():
        logger.info("✅ vLLM ya está corriendo")
        
        # Verificar modelos cargados
        llama_loaded = check_model_loaded(LLAMA_MODEL)
        deepseek_loaded = check_model_loaded(DEEPSEEK_MODEL)
        
        if llama_loaded:
            logger.info(f"✅ Modelo Llama cargado: {LLAMA_MODEL}")
        else:
            logger.warning(f"⚠️ Modelo Llama no está cargado: {LLAMA_MODEL}")
            logger.info("   Necesitas iniciar vLLM con este modelo manualmente")
        
        if deepseek_loaded:
            logger.info(f"✅ Modelo DeepSeek cargado: {DEEPSEEK_MODEL}")
        else:
            logger.warning(f"⚠️ Modelo DeepSeek no está cargado: {DEEPSEEK_MODEL}")
            logger.info("   Necesitas iniciar vLLM con este modelo manualmente")
        
        logger.info("\n💡 Nota: vLLM solo puede cargar un modelo a la vez.")
        logger.info("   Para cambiar de modelo, detén vLLM e inícialo con el modelo deseado.")
        logger.info(f"   Ejemplo: vllm serve {LLAMA_MODEL}")
        
    else:
        logger.warning("⚠️ vLLM no está corriendo")
        logger.info("\n📋 Instrucciones:")
        logger.info("1. Instala vLLM: pip install vllm")
        logger.info("2. Autentícate en Hugging Face: huggingface-cli login")
        logger.info(f"3. Inicia vLLM con Llama: vllm serve {LLAMA_MODEL}")
        logger.info(f"   O con DeepSeek: vllm serve {DEEPSEEK_MODEL}")
        logger.info("\n💡 Nota: La primera vez descargará el modelo automáticamente.")
        logger.info("   Esto puede tomar varios minutos dependiendo de tu conexión.")
        
        # Preguntar si quiere iniciar vLLM ahora (solo si hay stdin disponible)
        if sys.stdin.isatty():
            try:
                respuesta = input("\n¿Quieres iniciar vLLM con Llama ahora? (s/n): ").lower()
                if respuesta == 's':
                    process = start_vllm_with_model(LLAMA_MODEL)
                    if process:
                        logger.info("\n✅ vLLM iniciado en background")
                        logger.info("   Presiona Ctrl+C para detenerlo")
                        try:
                            process.wait()
                        except KeyboardInterrupt:
                            logger.info("\n🛑 Deteniendo vLLM...")
                            process.terminate()
            except (KeyboardInterrupt, EOFError):
                logger.info("\n👋 Saliendo...")
                sys.exit(0)
        else:
            logger.info("\n💡 Ejecuta este script de forma interactiva para iniciar vLLM automáticamente")
            logger.info(f"   O inicia vLLM manualmente: vllm serve {LLAMA_MODEL}")

if __name__ == "__main__":
    main()

