from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime
import subprocess
import tempfile
import logging
from llama_integration import LLMClient
import config

app = Flask(__name__)
CORS(app)

# Inicializar cliente LLM (vLLM)
llm_client = LLMClient()

# Configuración
DB_PATH = config.DB_PATH
LOG_FILE = config.LOG_FILE

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_db():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de configuración
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Tabla de conversaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de mensajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Base de datos inicializada")

def get_config(key, default=None):
    """Obtiene un valor de configuración"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else default

def set_config(key, value):
    """Establece un valor de configuración"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

@app.route('/api/config/user', methods=['GET'])
def get_user_name():
    """Obtiene el nombre de usuario"""
    username = get_config('username')
    return jsonify({'username': username})

@app.route('/api/config/user', methods=['POST'])
def set_user_name():
    """Establece el nombre de usuario"""
    data = request.json
    username = data.get('username')
    if username:
        set_config('username', username)
        logger.info(f"Nombre de usuario establecido: {username}")
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'error': 'Username requerido'}), 400

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Obtiene todas las conversaciones"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM conversations 
        ORDER BY updated_at DESC
    ''')
    conversations = []
    for row in cursor.fetchall():
        conversations.append({
            'id': row[0],
            'title': row[1],
            'created_at': row[2],
            'updated_at': row[3]
        })
    conn.close()
    return jsonify(conversations)

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Crea una nueva conversación"""
    data = request.json
    title = data.get('title', 'Nueva conversación')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversations (title) VALUES (?)', (title,))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Conversación creada: {conversation_id}")
    return jsonify({'id': conversation_id, 'title': title})

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Elimina una conversación"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
    cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    conn.commit()
    conn.close()
    logger.info(f"Conversación eliminada: {conversation_id}")
    return jsonify({'success': True})

@app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_messages(conversation_id):
    """Obtiene los mensajes de una conversación"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, role, content, created_at 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
    ''', (conversation_id,))
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'id': row[0],
            'role': row[1],
            'content': row[2],
            'created_at': row[3]
        })
    conn.close()
    return jsonify(messages)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Procesa un mensaje del chat"""
    data = request.json
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    username = get_config('username', 'Usuario')
    
    # Guardar mensaje del usuario
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if conversation_id:
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'user', message))
        cursor.execute('''
            UPDATE conversations SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (conversation_id,))
    else:
        # Crear nueva conversación
        cursor.execute('INSERT INTO conversations (title) VALUES (?)', (message[:50],))
        conversation_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'user', message))
    
    conn.commit()
    conn.close()
    
    # Procesar con Llama3B
    try:
        response = process_with_llama(message, username, conversation_id)
        
        # Guardar respuesta
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'assistant', response['content']))
        conn.commit()
        conn.close()
        
        return jsonify({
            'conversation_id': conversation_id,
            'response': response
        })
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}")
        return jsonify({'error': f'Error procesando mensaje: {str(e)}'}), 500

@app.route('/api/execute', methods=['POST'])
def execute_script():
    """Ejecuta un script generado"""
    data = request.json
    script_content = data.get('script')
    language = data.get('language', 'python')
    
    if not script_content:
        return jsonify({'error': 'Script requerido'}), 400
    
    try:
        result = run_script(script_content, language)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error ejecutando script: {str(e)}")
        return jsonify({'error': f'Error ejecutando script: {str(e)}'}), 500

def process_with_llama(message, username, conversation_id):
    """Procesa el mensaje con Llama usando vLLM"""
    # Obtener historial de la conversación
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
    ''', (conversation_id,))
    history = cursor.fetchall()
    conn.close()
    
    # Procesar con Llama usando vLLM
    response = llm_client.generate(message, None, history, username, use_deepseek=False)
    
    # Si necesita DeepSeek para generar código
    if response.get('needs_deepseek'):
        logger.info("Solicitando código a DeepSeek")
        
        # Construir contexto mejorado para DeepSeek basado en la respuesta de Llama
        # Llama razona y prepara instrucciones específicas para DeepSeek
        context_for_deepseek = f"""
Mensaje del usuario: {message}
Respuesta de análisis: {response.get('content', '')}
Historial de conversación relevante: {str(history[-3:]) if history else 'Ninguno'}
"""
        
        language = response.get('language', 'python')
        deepseek_requirements = response.get('content', message)
        
        # Usar DeepSeek para generar código
        deepseek_result = llm_client.generate_code_with_deepseek(
            requirements=deepseek_requirements,
            language=language,
            context=context_for_deepseek
        )
        
        if deepseek_result.get('success'):
            code = deepseek_result.get('code')
            language = deepseek_result.get('language', language)
            response['content'] += f"\n\nHe generado el siguiente código usando DeepSeek:\n\n```{language}\n{code}\n```"
            response['code'] = code
            response['language'] = language
            response['needs_code'] = True
        else:
            response['content'] += f"\n\n⚠️ No pude generar el código con DeepSeek: {deepseek_result.get('error', 'Error desconocido')}"
    
    return response

def run_script(script_content, language):
    """Ejecuta un script en el lenguaje especificado"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=get_file_extension(language)) as f:
        f.write(script_content)
        temp_file = f.name
    
    try:
        if language == 'python':
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif language == 'bash':
            result = subprocess.run(
                ['bash', temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
        elif language == 'c':
            # Compilar y ejecutar C
            compiled = temp_file.replace('.c', '')
            compile_result = subprocess.run(
                ['gcc', temp_file, '-o', compiled],
                capture_output=True,
                text=True,
                timeout=30
            )
            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': compile_result.stderr,
                    'error': 'Error de compilación'
                }
            result = subprocess.run(
                [compiled],
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            return {'success': False, 'error': f'Lenguaje no soportado: {language}'}
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def get_file_extension(language):
    """Obtiene la extensión de archivo para un lenguaje"""
    extensions = {
        'python': '.py',
        'bash': '.sh',
        'c': '.c',
        'rust': '.rs',
        'go': '.go'
    }
    return extensions.get(language, '.txt')

if __name__ == '__main__':
    init_db()
    app.run(debug=config.FLASK_DEBUG, host=config.FLASK_HOST, port=config.FLASK_PORT)

