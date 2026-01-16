from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime, timedelta
import subprocess
import tempfile
import logging
import jwt
import bcrypt
from functools import wraps
from llama_integration import LLMClient
import config

app = Flask(__name__)
CORS(app)

# Inicializar cliente LLM (vLLM)
llm_client = LLMClient()

# Configuración
DB_PATH = config.DB_PATH
LOG_FILE = config.LOG_FILE
JWT_SECRET = os.getenv('JWT_SECRET', 'tu-secret-key-cambiar-en-produccion')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

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
    
    # Tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            language TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migración: agregar columna language si no existe
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT NULL')
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    
    # Tabla de conversaciones (ahora con user_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
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

def generate_token(user_id, username):
    """Genera un token JWT para el usuario"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """Verifica y decodifica un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_from_token():
    """Obtiene el usuario del token en el header Authorization"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]  # Bearer <token>
        payload = verify_token(token)
        if payload:
            return {
                'user_id': payload['user_id'],
                'username': payload['username']
            }
    except:
        pass
    return None

def require_auth(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_token()
        if not user:
            return jsonify({'error': 'No autorizado. Token requerido.'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud para verificar que el backend está funcionando"""
    return jsonify({'status': 'ok', 'service': 'chat-backend'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registra un nuevo usuario"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar si el usuario o email ya existen
    cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'El usuario o email ya existe'}), 400
    
    # Hash de la contraseña
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Crear usuario (sin idioma inicialmente, se pedirá después)
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, language)
        VALUES (?, ?, ?, NULL)
    ''', (username, email, password_hash))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Generar token
    token = generate_token(user_id, username)
    
    logger.info(f"Usuario registrado: {username} ({email}) - pendiente selección de idioma")
    return jsonify({
        'success': True,
        'token': token,
        'needs_language': True,  # Indicar que necesita seleccionar idioma
        'user': {
            'id': user_id,
            'username': username,
            'email': email,
            'language': None
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Inicia sesión de un usuario"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar usuario por email
    cursor.execute('SELECT id, username, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    user_id, username, password_hash = user
    
    # Verificar contraseña
    if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
        return jsonify({'error': 'Credenciales inválidas'}), 401
    
    # Generar token
    token = generate_token(user_id, username)
    
    # Obtener idioma del usuario
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE id = ?', (user_id,))
    language_result = cursor.fetchone()
    language = language_result[0] if language_result and language_result[0] else None
    conn.close()
    
    logger.info(f"Usuario inició sesión: {username} ({email}), idioma: {language}")
    return jsonify({
        'success': True,
        'token': token,
        'needs_language': language is None,  # Si no tiene idioma, necesita seleccionarlo
        'user': {
            'id': user_id,
            'username': username,
            'email': email,
            'language': language
        }
    })

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Obtiene la información del usuario actual"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, language FROM users WHERE id = ?', (user['user_id'],))
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify({
        'id': user_data[0],
        'username': user_data[1],
        'email': user_data[2],
        'language': user_data[3] if len(user_data) > 3 else None,
        'needs_language': user_data[3] is None if len(user_data) > 3 else True
    })

@app.route('/api/auth/language', methods=['POST'])
@require_auth
def set_language():
    """Establece el idioma del usuario"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    language = data.get('language')
    
    if language not in ['es', 'en']:
        return jsonify({'error': 'Idioma inválido. Use "es" o "en"'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE id = ?', (language, user['user_id']))
    conn.commit()
    conn.close()
    
    logger.info(f"Idioma establecido para usuario {user['username']}: {language}")
    return jsonify({
        'success': True,
        'language': language
    })

@app.route('/api/conversations', methods=['GET'])
@require_auth
def get_conversations():
    """Obtiene todas las conversaciones del usuario actual"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM conversations 
        WHERE user_id = ?
        ORDER BY updated_at DESC
    ''', (user['user_id'],))
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
@require_auth
def create_conversation():
    """Crea una nueva conversación para el usuario actual"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    title = data.get('title', 'Nueva conversación')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO conversations (user_id, title) VALUES (?, ?)', (user['user_id'], title))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"Conversación creada: {conversation_id} para usuario {user['username']}")
    return jsonify({'id': conversation_id, 'title': title})

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
@require_auth
def delete_conversation(conversation_id):
    """Elimina una conversación del usuario actual"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Verificar que la conversación pertenece al usuario
    cursor.execute('SELECT id FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user['user_id']))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Conversación no encontrada'}), 404
    
    cursor.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
    cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    conn.commit()
    conn.close()
    logger.info(f"Conversación eliminada: {conversation_id} por usuario {user['username']}")
    return jsonify({'success': True})

@app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
@require_auth
def get_messages(conversation_id):
    """Obtiene los mensajes de una conversación del usuario actual"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Verificar que la conversación pertenece al usuario
    cursor.execute('SELECT id FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user['user_id']))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Conversación no encontrada'}), 404
    
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
@require_auth
def chat():
    """Procesa un mensaje del chat"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
    data = request.json
    message = data.get('message')
    conversation_id = data.get('conversation_id')
    
    if not message:
        return jsonify({'error': 'Mensaje requerido'}), 400
    
    username = user['username']
    
    # Guardar mensaje del usuario
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if conversation_id:
        # Verificar que la conversación pertenece al usuario
        cursor.execute('SELECT id FROM conversations WHERE id = ? AND user_id = ?', (conversation_id, user['user_id']))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'user', message))
        cursor.execute('''
            UPDATE conversations SET updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (conversation_id,))
    else:
        # Crear nueva conversación para el usuario
        cursor.execute('INSERT INTO conversations (user_id, title) VALUES (?, ?)', (user['user_id'], message[:50]))
        conversation_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'user', message))
    
    conn.commit()
    conn.close()
    
    # Procesar con Llama usando Ollama
    try:
        response = process_with_llama(message, username, conversation_id, user['user_id'])
        
        # Guardar respuesta
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content) 
            VALUES (?, ?, ?)
        ''', (conversation_id, 'assistant', response.get('content', 'Error al generar respuesta')))
        conn.commit()
        conn.close()
        
        return jsonify({
            'conversation_id': conversation_id,
            'response': response
        })
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
        error_message = str(e)
        
        # Guardar mensaje de error
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            error_content = f"Error al procesar el mensaje: {error_message}"
            cursor.execute('''
                INSERT INTO messages (conversation_id, role, content) 
                VALUES (?, ?, ?)
            ''', (conversation_id, 'assistant', error_content))
            conn.commit()
            conn.close()
        except Exception as db_error:
            logger.error(f"Error guardando mensaje de error en BD: {str(db_error)}")
        
        return jsonify({
            'conversation_id': conversation_id,
            'response': {
                'content': error_content,
                'needs_code': False,
                'code': None,
                'language': None
            },
            'error': error_message
        }), 500

@app.route('/api/execute', methods=['POST'])
@require_auth
def execute_script():
    """Ejecuta un script generado"""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'No autorizado'}), 401
    
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

def process_with_llama(message, username, conversation_id, user_id=None):
    """Procesa el mensaje con Llama usando Ollama"""
    # Obtener historial de la conversación y idioma del usuario
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, content FROM messages 
        WHERE conversation_id = ? 
        ORDER BY created_at ASC
    ''', (conversation_id,))
    history = cursor.fetchall()
    
    # Obtener idioma del usuario
    user_language = 'es'  # Por defecto español
    if user_id:
        cursor.execute('SELECT language FROM users WHERE id = ?', (user_id,))
        lang_result = cursor.fetchone()
        if lang_result and lang_result[0]:
            user_language = lang_result[0]
        else:
            logger.warning(f"Usuario {user_id} no tiene idioma configurado, usando español por defecto")
    
    logger.info(f"Procesando mensaje para usuario {user_id} ({username}) en idioma: {user_language}")
    conn.close()
    
    # Procesar con Llama usando Ollama
    response = llm_client.generate(message, None, history, username, language=user_language, use_deepseek=False)
    
    # Si detecta comandos del sistema, ejecutarlos directamente
    if response.get('needs_code') and response.get('is_system_command'):
        command = response.get('code')
        logger.info(f"Ejecutando comando del sistema: {command}")
        try:
            command_result = run_system_command(command)
            if command_result.get('success'):
                output = command_result.get('output', '').strip()
                # Mantener solo la primera línea/frase de la respuesta original
                first_line = response['content'].split('\n')[0]
                response['content'] = first_line
                
                # Si se instaló algo, mencionarlo
                if command_result.get('install_attempted'):
                    missing_cmd = command_result.get('missing_command', 'herramienta')
                    package = command_result.get('package_installed', missing_cmd)
                    response['content'] += f"\n\n📦 {missing_cmd} no estaba instalado. Instalando {package}..."
                    response['content'] += f"\n✅ Instalación completada. Reintentando comando..."
                
                if output:
                    response['content'] += f"\n\n{output}"
                else:
                    response['content'] += "\n✅ Ejecutado"
            else:
                error = command_result.get('error', 'Error desconocido')
                # Mantener solo la primera línea y agregar error
                first_line = response['content'].split('\n')[0]
                response['content'] = first_line
                
                # Si se intentó instalar pero falló
                if command_result.get('install_attempted'):
                    if command_result.get('install_failed'):
                        response['content'] += f"\n\n⚠️ Error instalando herramienta: {error}"
                    else:
                        response['content'] += f"\n\n❌ {error}"
                else:
                    response['content'] += f"\n❌ {error}"
            # No necesita código para ejecutar, ya se ejecutó
            response['needs_code'] = False
        except Exception as e:
            logger.error(f"Error ejecutando comando: {str(e)}")
            first_line = response['content'].split('\n')[0] if response.get('content') else "Error"
            response['content'] = first_line + f"\n❌ Error: {str(e)}"
            response['needs_code'] = False
    
    # También verificar si hay comandos en el texto aunque no se detectaron como código
    elif not response.get('needs_code'):
        # Buscar comandos directamente en el contenido de la respuesta
        import re
        system_commands_pattern = r'\b(nmap|ping|curl|wget|ss|tcpdump|netstat|grep|find|ps|top|iptables|systemctl|service|journalctl|whois|dig|nslookup|arp|route|ifconfig|ip)\s+[^\n`]+'
        command_match = re.search(system_commands_pattern, response.get('content', ''), re.IGNORECASE)
        if command_match:
            command = command_match.group(0).strip()
            command = re.sub(r'[.,;:!?]+$', '', command).strip()
            if len(command.split()) > 1:
                logger.info(f"Comando detectado en texto, ejecutando: {command}")
                try:
                    command_result = run_system_command(command)
                    if command_result.get('success'):
                        output = command_result.get('output', '').strip()
                        first_line = response['content'].split('\n')[0]
                        response['content'] = first_line
                        
                        # Si se instaló algo, mencionarlo
                        if command_result.get('install_attempted'):
                            missing_cmd = command_result.get('missing_command', 'herramienta')
                            package = command_result.get('package_installed', missing_cmd)
                            response['content'] += f"\n\n📦 {missing_cmd} no estaba instalado. Instalando {package}..."
                            response['content'] += f"\n✅ Instalación completada. Reintentando comando..."
                        
                        if output:
                            response['content'] += f"\n\n{output}"
                    else:
                        error = command_result.get('error', 'Error desconocido')
                        first_line = response['content'].split('\n')[0]
                        response['content'] = first_line
                        
                        # Si se intentó instalar pero falló
                        if command_result.get('install_attempted'):
                            if command_result.get('install_failed'):
                                response['content'] += f"\n\n⚠️ Error instalando herramienta: {error}"
                            else:
                                response['content'] += f"\n\n❌ {error}"
                        else:
                            response['content'] += f"\n❌ {error}"
                except Exception as e:
                    logger.error(f"Error ejecutando comando detectado: {str(e)}")
    
    # Si necesita DeepSeek para generar código
    elif response.get('needs_deepseek'):
        logger.info("Solicitando código a DeepSeek")
        
        # Construir contexto mejorado para DeepSeek basado en la respuesta de Llama
        context_for_deepseek = f"""
Mensaje del usuario: {message}
Respuesta de análisis: {response.get('content', '')}
Historial de conversación relevante: {str(history[-3:]) if history else 'Ninguno'}
"""
        
        language = response.get('language', 'python')
        deepseek_requirements = response.get('content', message)
        
        # Usar DeepSeek para generar código (user_language ya se obtuvo arriba)
        deepseek_result = llm_client.generate_code_with_deepseek(
            requirements=deepseek_requirements,
            language=language,
            context=context_for_deepseek,
            user_language=user_language  # Reutilizar la variable ya obtenida
        )
        
        if deepseek_result.get('success'):
            code = deepseek_result.get('code')
            language = deepseek_result.get('language', language)
            response['content'] += f"\n\n```{language}\n{code}\n```"
            response['code'] = code
            response['language'] = language
            response['needs_code'] = True
        else:
            response['content'] += f"\n\n⚠️ No pude generar el código con DeepSeek: {deepseek_result.get('error', 'Error desconocido')}"
    
    return response

def get_package_for_command(command_name):
    """Mapea un comando a su paquete de instalación"""
    # Mapeo de comandos comunes de Kali Linux a sus paquetes
    command_to_package = {
        'nmap': 'nmap',
        'tcpdump': 'tcpdump',
        'wireshark': 'wireshark',
        'aircrack-ng': 'aircrack-ng',
        'hydra': 'hydra',
        'john': 'john',
        'hashcat': 'hashcat',
        'metasploit': 'metasploit-framework',
        'sqlmap': 'sqlmap',
        'nikto': 'nikto',
        'dirb': 'dirb',
        'gobuster': 'gobuster',
        'ffuf': 'ffuf',
        'burpsuite': 'burpsuite',
        'wpscan': 'wpscan',
        'enum4linux': 'enum4linux',
        'smbclient': 'smbclient',
        'impacket': 'python3-impacket',
        'netcat': 'netcat',
        'nc': 'netcat',
        'ncat': 'nmap',  # ncat viene con nmap
        'curl': 'curl',
        'wget': 'wget',
        'git': 'git',
        'python3': 'python3',
        'python': 'python3',
        'pip': 'python3-pip',
        'pip3': 'python3-pip',
        'gcc': 'gcc',
        'g++': 'g++',
        'make': 'make',
        'rustc': 'rustc',
        'cargo': 'cargo',
        'go': 'golang-go',
        'docker': 'docker.io',
        'kubectl': 'kubectl',
        'whois': 'whois',
        'dig': 'dnsutils',
        'nslookup': 'dnsutils',
        'ss': 'iproute2',  # ss viene con iproute2
        'ip': 'iproute2',
        'ifconfig': 'net-tools',
        'netstat': 'net-tools',
        'arp': 'net-tools',
        'route': 'net-tools',
        'iptables': 'iptables',
        'ufw': 'ufw',
        'systemctl': 'systemd',  # Ya viene instalado en la mayoría de sistemas
        'service': 'systemd',
        'journalctl': 'systemd',
        'lsof': 'lsof',
        'fuser': 'psmisc',
        'killall': 'psmisc',
        'htop': 'htop',
        'vim': 'vim',
        'nano': 'nano',
        'tmux': 'tmux',
        'screen': 'screen',
        'zsh': 'zsh',
        'fish': 'fish',
    }
    
    # Limpiar el comando (quitar sudo, argumentos, etc.)
    cmd_clean = command_name.strip().lower()
    if cmd_clean.startswith('sudo '):
        cmd_clean = cmd_clean[5:]
    
    # Obtener solo el primer comando (antes del primer espacio)
    cmd_base = cmd_clean.split()[0] if cmd_clean.split() else cmd_clean
    
    return command_to_package.get(cmd_base, cmd_base)

def detect_missing_command(error_message):
    """Detecta si el error indica que falta un comando"""
    if not error_message:
        return None
    
    error_lower = error_message.lower()
    
    # Patrones comunes de "comando no encontrado"
    patterns = [
        r"command not found",
        r"comando no encontrado",
        r"no se encontró",
        r"not found",
        r"no such file or directory",
        r"no se puede ejecutar",
        r"cannot execute",
    ]
    
    for pattern in patterns:
        if pattern in error_lower:
            # Intentar extraer el nombre del comando del error
            import re
            # Buscar patrones como "nmap: command not found" o "command 'nmap' not found"
            cmd_match = re.search(r"['\"]?(\w+):?\s*(?:command|comando)", error_lower)
            if cmd_match:
                return cmd_match.group(1)
            # Buscar en formato "command 'nmap' not found"
            cmd_match2 = re.search(r"command\s+['\"](\w+)['\"]", error_lower)
            if cmd_match2:
                return cmd_match2.group(1)
    
    return None

def install_package(package_name):
    """Instala un paquete usando apt"""
    try:
        logger.info(f"Instalando paquete: {package_name}")
        
        # Ejecutar actualización e instalación
        install_command = f"sudo apt update && sudo apt install -y {package_name}"
        
        result = subprocess.run(
            install_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos para instalación
            env=os.environ.copy()
        )
        
        if result.returncode == 0:
            logger.info(f"Paquete {package_name} instalado correctamente")
            return {
                'success': True,
                'output': result.stdout,
                'package': package_name
            }
        else:
            logger.error(f"Error instalando {package_name}: {result.stderr}")
            return {
                'success': False,
                'error': result.stderr,
                'package': package_name
            }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Instalación excedió el tiempo límite (5 minutos)',
            'package': package_name
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'package': package_name
        }

def run_system_command(command, retry_after_install=True):
    """Ejecuta un comando del sistema directamente, con soporte para sudo y auto-instalación"""
    try:
        # Detectar si el comando ya incluye sudo
        command_str = command if isinstance(command, str) else ' '.join(command)
        original_command = command_str
        
        # Si el comando requiere permisos elevados pero no tiene sudo, agregarlo
        commands_requiring_root = ['nmap', 'ss', 'tcpdump', 'netstat', 'iptables', 
                                   'systemctl', 'service', 'journalctl', 'ps aux',
                                   'lsof', 'fuser', 'killall']
        
        needs_sudo = False
        if not command_str.startswith('sudo '):
            for cmd in commands_requiring_root:
                if command_str.strip().startswith(cmd):
                    needs_sudo = True
                    break
        
        # Ejecutar con sudo si es necesario (usando sudo sin contraseña si está configurado)
        if needs_sudo and not command_str.startswith('sudo '):
            command_str = f"sudo {command_str}"
            logger.info(f"Agregando sudo al comando: {command_str}")
        
        result = subprocess.run(
            command_str,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            # Permitir ejecutar como root si es necesario
            env=os.environ.copy()
        )
        
        # Si falló y el error indica que falta un comando, intentar instalarlo
        if result.returncode != 0 and retry_after_install:
            missing_command = detect_missing_command(result.stderr or result.stdout)
            
            if missing_command:
                logger.info(f"Comando faltante detectado: {missing_command}")
                package_name = get_package_for_command(missing_command)
                
                if package_name:
                    logger.info(f"Instalando paquete: {package_name}")
                    install_result = install_package(package_name)
                    
                    if install_result.get('success'):
                        # Reintentar el comando original después de instalar
                        logger.info(f"Reintentando comando después de instalar {package_name}: {original_command}")
                        retry_result = run_system_command(original_command, retry_after_install=False)
                        # Marcar que se instaló y se reintentó
                        retry_result['install_attempted'] = True
                        retry_result['missing_command'] = missing_command
                        retry_result['package_installed'] = package_name
                        return retry_result
                    else:
                        # Si la instalación falló, devolver ambos errores
                        return {
                            'success': False,
                            'output': result.stdout,
                            'error': f"Error ejecutando comando: {result.stderr}\nError instalando {package_name}: {install_result.get('error')}",
                            'missing_command': missing_command,
                            'install_attempted': True,
                            'install_failed': True
                        }
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Comando excedió el tiempo límite (60 segundos)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

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

