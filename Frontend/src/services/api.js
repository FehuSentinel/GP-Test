import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 segundos de timeout
});

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      console.error('Error de conexión: El backend no está disponible');
      return Promise.reject(new Error('No se puede conectar con el servidor. Asegúrate de que el backend esté corriendo en http://localhost:5000'));
    }
    return Promise.reject(error);
  }
);

// Configuración
export const checkUsername = async () => {
  const response = await api.get('/config/user');
  return response.data;
};

export const setUsername = async (username) => {
  const response = await api.post('/config/user', { username });
  return response.data;
};

// Conversaciones
export const getConversations = async () => {
  const response = await api.get('/conversations');
  return response.data;
};

export const createConversation = async (title = 'Nueva conversación') => {
  const response = await api.post('/conversations', { title });
  return response.data;
};

export const deleteConversation = async (id) => {
  const response = await api.delete(`/conversations/${id}`);
  return response.data;
};

// Mensajes
export const getMessages = async (conversationId) => {
  const response = await api.get(`/conversations/${conversationId}/messages`);
  return response.data;
};

export const sendMessage = async (message, conversationId = null) => {
  const response = await api.post('/chat', {
    message,
    conversation_id: conversationId,
  });
  return response.data;
};

// Ejecución de scripts
export const executeScript = async (script, language) => {
  const response = await api.post('/execute', {
    script,
    language,
  });
  return response.data;
};

