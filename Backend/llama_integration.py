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
                        "temperature": 0.6,  # Balance entre determinismo y creatividad para interactividad
                        "num_predict": 300,  # Respuestas MUY cortas (máximo ~300 tokens)
                        "num_ctx": 2048,  # Contexto reducido
                        "num_thread": 2,  # Menos threads para menos CPU
                        "repeat_penalty": 1.3,  # Evita repeticiones
                        "top_p": 0.9,  # Más enfocado
                        "top_k": 40  # Menos opciones, más directo
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
                    'needs_deepseek': code_info.get('needs_deepseek', False),
                    'is_system_command': code_info.get('is_system_command', False)
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
        """Construye el prompt del sistema interactivo y conciso"""
        return f"""Eres asistente técnico interactivo para {username}. Sé breve, analiza y ejecuta.

ESTILO DE RESPUESTA:
- Saludo breve: "Claro", "Vale", "Perfecto", "Empecemos"
- Analiza rápidamente qué necesita el usuario
- Si falta información crítica, pregunta UNA pregunta corta
- Si tienes suficiente info, ejecuta directamente
- Máximo 2-3 frases TOTALES por respuesta

EJECUCIÓN:
- Comandos del sistema (nmap, ping, curl, etc.): escríbelos directamente en tu respuesta
- Los comandos se ejecutarán automáticamente, NO necesitas explicar cómo
- Después del comando, di brevemente qué esperas ver

INTERACTIVIDAD:
- Si el usuario dice "escanea IP" sin especificar puertos → pregunta: "¿Todos los puertos o específicos?"
- Si dice "genera script" sin detalles → pregunta: "¿Qué debe hacer el script exactamente?"
- Si tienes toda la info → ejecuta sin preguntar

EJEMPLOS CORRECTOS:
Usuario: "escanea 10.129.23.10 con nmap rápido todos los puertos"
Tú: "Claro. Escaneando todos los puertos...\nnmap -sS -sV -p- 10.129.23.10"

Usuario: "escanea esta IP"
Tú: "¿Qué puertos quieres escanear? ¿Todos o específicos?"

Usuario: "ping google"
Tú: "Vale.\nping -c 4 8.8.8.8"

PROHIBIDO:
- Explicar cómo funcionan las herramientas
- Dar pasos de instalación
- Más de 3 frases
- Explicaciones técnicas innecesarias

Sé conversacional pero eficiente. Analiza → Pregunta si falta info → Ejecuta."""
    
    def _analyze_response(self, response_text):
        """
        Analiza la respuesta para detectar código, comandos del sistema o necesidad de DeepSeek
        """
        # Detectar comandos del sistema directamente en el texto (nmap, ping, etc.)
        system_commands = ['nmap', 'ping', 'curl', 'wget', 'netstat', 'ss', 'tcpdump', 
                          'grep', 'find', 'ls', 'cat', 'tail', 'head', 'ps', 'top',
                          'iptables', 'ufw', 'systemctl', 'service', 'journalctl', 'whois',
                          'dig', 'nslookup', 'arp', 'route', 'ifconfig', 'ip']
        
        # Buscar comandos del sistema en el texto (formato: comando + argumentos)
        for cmd in system_commands:
            pattern = r'\b' + re.escape(cmd) + r'\s+[^\n`]+'
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                command_line = match.group(0).strip()
                # Limpiar el comando (quitar puntuación al final si es solo explicación)
                command_line = re.sub(r'[.,;:!?]+$', '', command_line).strip()
                # Verificar que no sea solo una mención en texto explicativo
                if len(command_line.split()) > 1:  # Tiene argumentos, es un comando real
                    return True, {
                        'code': command_line,
                        'language': 'bash',
                        'is_system_command': True,
                        'needs_deepseek': False
                    }
        
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
                'needs_deepseek': needs_deepseek,
                'is_system_command': False
            }
        
        return False, {'needs_deepseek': needs_deepseek, 'is_system_command': False}

# Mantener compatibilidad con nombre anterior
Llama3BClient = LLMClient
