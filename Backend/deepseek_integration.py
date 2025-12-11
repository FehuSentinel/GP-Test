"""
Integración con DeepSeek API para generación de código
"""
import logging
import requests
import json
import os

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self, api_key=None):
        """
        Inicializa el cliente de DeepSeek
        La API key puede venir de variable de entorno DEEPSEEK_API_KEY
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
    
    def generate_code(self, requirements, language="python", context=""):
        """
        Genera código usando DeepSeek API
        
        Args:
            requirements: Descripción de lo que necesita el código
            language: Lenguaje de programación
            context: Contexto adicional sobre lo que se necesita
        
        Returns:
            dict con el código generado y metadatos
        """
        if not self.api_key:
            logger.warning("DeepSeek API key no configurada")
            return {
                'success': False,
                'error': 'DeepSeek API key no configurada',
                'code': None
            }
        
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

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un experto programador que genera código limpio, eficiente y seguro."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                code_content = result['choices'][0]['message']['content']
                
                # Extraer código si viene en bloques markdown
                import re
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
                logger.error(f"Error en DeepSeek API: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Error en DeepSeek API: {response.status_code}',
                    'code': None
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con DeepSeek: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}',
                'code': None
            }

