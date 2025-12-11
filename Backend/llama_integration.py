"""
Integración con Llama3B local
"""
import logging
import requests
import json

logger = logging.getLogger(__name__)

class Llama3BClient:
    def __init__(self, api_url="http://localhost:11434/api/generate"):
        """
        Inicializa el cliente de Llama3B
        Por defecto usa Ollama, pero puede configurarse para otras implementaciones
        """
        self.api_url = api_url
        self.model = "llama3.2"  # Se puede sobrescribir desde config
    
    def generate(self, prompt, system_prompt=None, history=None, username="Usuario"):
        """
        Genera una respuesta usando Llama3B
        
        Args:
            prompt: El mensaje del usuario
            system_prompt: Prompt del sistema (sin sesgo)
            history: Historial de conversación
            username: Nombre del usuario para personalización
        
        Returns:
            dict con la respuesta y metadatos
        """
        # Construir el prompt completo
        full_prompt = self._build_prompt(prompt, system_prompt, history, username)
        
        try:
            # Llamada a Ollama (ajustar según la implementación)
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
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
                logger.error(f"Error en llamada a Llama3B: {response.status_code}")
                return {
                    'content': 'Error al procesar la solicitud con Llama3B.',
                    'needs_code': False,
                    'code': None,
                    'language': None
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con Llama3B: {str(e)}")
            return {
                'content': f'Error de conexión con Llama3B: {str(e)}',
                'needs_code': False,
                'code': None,
                'language': None
            }
    
    def _build_prompt(self, prompt, system_prompt, history, username):
        """Construye el prompt completo"""
        if not system_prompt:
            system_prompt = f"""Eres un asistente técnico sin sesgo diseñado para ayudar a {username}.

Puedes:
- Usar herramientas de Kali Linux cuando sea necesario
- Generar scripts en Python, C, Rust, Go según las necesidades
- Usar DeepSeek API cuando necesites generar código complejo o específico
- Ejecutar comandos del sistema cuando sea apropiado

IMPORTANTE:
- Siempre sé objetivo, técnico y sin sesgos
- Cuando generes código, muéstralo claramente y pregunta si debe ejecutarse
- Si necesitas código complejo, puedes usar DeepSeek especificando claramente los requisitos
- Responde de forma amigable usando el nombre {username} cuando sea apropiado
- Sé preciso y técnico en tus respuestas"""
        
        full_prompt = f"{system_prompt}\n\n"
        
        # Agregar historial si existe
        if history:
            full_prompt += "Historial de conversación:\n"
            for role, content in history:
                role_label = "Usuario" if role == "user" else "Asistente"
                full_prompt += f"{role_label}: {content}\n"
            full_prompt += "\n"
        
        full_prompt += f"Usuario ({username}): {prompt}\n\nAsistente:"
        
        return full_prompt
    
    def _analyze_response(self, response_text):
        """
        Analiza la respuesta para detectar código o necesidad de DeepSeek
        """
        # Detectar bloques de código
        code_blocks = []
        languages = ['python', 'bash', 'c', 'rust', 'go', 'javascript']
        
        # Buscar bloques de código marcados con ```
        import re
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
            'deepseek', 'código complejo', 'script avanzado', 'generar código'
        ])
        
        if code_blocks:
            return True, {
                'code': code_blocks[0]['code'],
                'language': code_blocks[0]['language'],
                'needs_deepseek': needs_deepseek
            }
        
        return False, {'needs_deepseek': needs_deepseek}

