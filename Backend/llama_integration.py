"""
Integración con modelos LLM usando Ollama (más estable que vLLM)
Soporta Llama y DeepSeek localmente
"""
import logging
import requests
import json
import re

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_url=None, chat_url=None, llama_model=None, deepseek_model=None):
        """
        Inicializa el cliente LLM usando Ollama
        
        Args:
            api_url: URL del servidor Ollama para generate
            chat_url: URL del servidor Ollama para chat
            llama_model: Modelo de Llama a usar
            deepseek_model: Modelo de DeepSeek a usar
        """
        import config
        self.api_url = api_url or config.OLLAMA_API_URL
        self.chat_url = chat_url or config.OLLAMA_CHAT_URL
        self.llama_model = llama_model or config.LLAMA_MODEL
        self.deepseek_model = deepseek_model or config.DEEPSEEK_MODEL
    
    def generate(self, prompt, system_prompt=None, history=None, username="Usuario", use_deepseek=False):
        """
        Genera una respuesta usando Llama o DeepSeek según corresponda
        
        Args:
            prompt: El mensaje del usuario
            system_prompt: Prompt del sistema (sin sesgo)
            history: Historial de conversación
            username: Nombre del usuario para personalización
            use_deepseek: Si True, usa DeepSeek en lugar de Llama
        
        Returns:
            dict con la respuesta y metadatos
        """
        model = self.deepseek_model if use_deepseek else self.llama_model
        
        # Construir mensajes en formato Ollama
        messages = []
        
        # System prompt
        if not system_prompt:
            system_prompt = self._build_system_prompt(username)
        
        # Historial de conversación
        if history:
            for role, content in history:
                messages.append({
                    "role": role if role in ["user", "assistant"] else "user",
                    "content": content
                })
        
        # Mensaje actual
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Llamada a Ollama usando API de chat (más estable)
            # Configuración optimizada para bajo consumo de recursos
            response = requests.post(
                self.chat_url,
                json={
                    "model": model,
                    "messages": messages,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.5,  # Más determinista, menos creativo
                        "num_predict": 500,  # Respuestas más cortas y directas
                        "num_ctx": 2048,  # Contexto reducido
                        "num_thread": 2,  # Menos threads para menos CPU
                        "repeat_penalty": 1.2  # Evita repeticiones
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('message', {}).get('content', '')
                
                # Analizar si la respuesta contiene código o necesita DeepSeek
                needs_code, code_info = self._analyze_response(response_text)
                
                return {
                    'content': response_text,
                    'needs_code': needs_code,
                    'code': code_info.get('code') if needs_code else None,
                    'language': code_info.get('language') if needs_code else None,
                    'needs_deepseek': code_info.get('needs_deepseek', False)
                }
            else:
                logger.error(f"Error en llamada a Ollama: {response.status_code} - {response.text}")
                return {
                    'content': f'Error al procesar la solicitud: {response.status_code}',
                    'needs_code': False,
                    'code': None,
                    'language': None
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Ollama: {str(e)}")
            return {
                'content': f'Error de conexión con Ollama: {str(e)}. Asegúrate de que Ollama esté corriendo (ollama serve).',
                'needs_code': False,
                'code': None,
                'language': None
            }
    
    def generate_code_with_deepseek(self, requirements, language="python", context=""):
        """
        Genera código usando DeepSeek específicamente para generación de código
        
        Args:
            requirements: Descripción de lo que necesita el código
            language: Lenguaje de programación
            context: Contexto adicional
        
        Returns:
            dict con el código generado
        """
        prompt = f"""Genera código en {language} con las siguientes especificaciones:

Requisitos:
{requirements}

Contexto adicional:
{context}

IMPORTANTE:
- El código debe ser funcional y bien estructurado
- Incluye comentarios cuando sea necesario
- Asegúrate de que el código sea seguro y eficiente
- Si es un script ejecutable, incluye manejo de errores apropiado

Genera SOLO el código, sin explicaciones adicionales a menos que sea necesario para claridad."""

        system_prompt = "Eres un experto programador que genera código limpio, eficiente y seguro."

        messages = [
            {"role": "user", "content": prompt}
        ]

        try:
            response = requests.post(
                self.chat_url,
                json={
                    "model": self.deepseek_model,
                    "messages": messages,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 800,  # Código más conciso
                        "num_ctx": 2048,  # Contexto reducido
                        "num_thread": 2,  # Menos threads para menos CPU
                        "repeat_penalty": 1.2  # Evita repeticiones
                    }
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                code_content = result.get('message', {}).get('content', '')
                
                # Extraer código si viene en bloques markdown
                code_pattern = r'```(?:\w+)?\n?(.*?)```'
                code_matches = re.findall(code_pattern, code_content, re.DOTALL)
                
                if code_matches:
                    code = code_matches[0].strip()
                else:
                    code = code_content.strip()
                
                return {
                    'success': True,
                    'code': code,
                    'language': language,
                    'raw_response': code_content
                }
            else:
                logger.error(f"Error en DeepSeek Ollama: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Error en DeepSeek: {response.status_code}',
                    'code': None
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con DeepSeek: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'code': None
            }
    
    def _build_system_prompt(self, username):
        """Construye el prompt del sistema sin sesgo, directo y conciso"""
        return f"""Eres un asistente técnico directo y eficiente para {username}.

REGLAS:
- Responde de forma concisa y directa. Sin explicaciones largas.
- Si pides algo, di QUÉ harás y CÓMO, sin rodeos.
- Sé conversacional pero técnico. No te explayes.
- Código: muéstralo y pregunta si ejecutar. Sin explicaciones extensas.
- Usa herramientas de Kali Linux cuando sea necesario.
- Genera scripts en Python, C, Rust, Go según necesidad.
- Para código complejo, usa DeepSeek.

FORMATO:
- Pregunta directa → Respuesta directa con acción.
- Si necesitas aclarar algo, pregunta brevemente.
- Máximo 2-3 frases de contexto antes de la acción.

Ejemplo:
Usuario: "escanea esta IP"
Tú: "Escaneando 10.129.23.10 con nmap -sS -sV -p- ... [resultado]"

Sé directo, técnico y eficiente."""
    
    def _analyze_response(self, response_text):
        """
        Analiza la respuesta para detectar código o necesidad de DeepSeek
        """
        # Detectar bloques de código
        code_blocks = []
        languages = ['python', 'bash', 'c', 'rust', 'go', 'javascript']
        
        # Buscar bloques de código marcados con ```
        code_pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(code_pattern, response_text, re.DOTALL)
        
        if matches:
            for lang, code in matches:
                lang = lang.lower() if lang else 'python'
                if lang in languages:
                    code_blocks.append({
                        'language': lang,
                        'code': code.strip()
                    })
        
        # Detectar si menciona DeepSeek o necesita código complejo
        needs_deepseek = any(keyword in response_text.lower() for keyword in [
            'deepseek', 'código complejo', 'script avanzado', 'generar código', 'usar deepseek'
        ])
        
        if code_blocks:
            return True, {
                'code': code_blocks[0]['code'],
                'language': code_blocks[0]['language'],
                'needs_deepseek': needs_deepseek
            }
        
        return False, {'needs_deepseek': needs_deepseek}

# Mantener compatibilidad con nombre anterior
Llama3BClient = LLMClient
