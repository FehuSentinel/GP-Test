import React, { useState, useEffect, useRef } from 'react';
import './ChatArea.css';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import CodeExecutionModal from './CodeExecutionModal';
import { getMessages, sendMessage, executeScript } from '../services/api';

function ChatArea({ conversationId, username }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [codeToExecute, setCodeToExecute] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (conversationId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadMessages = async () => {
    try {
      const data = await getMessages(conversationId);
      setMessages(data);
    } catch (error) {
      console.error('Error cargando mensajes:', error);
    }
  };

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await sendMessage(message, conversationId);
      
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response.content,
        created_at: new Date().toISOString(),
        needs_code: response.response.needs_code,
        code: response.response.code,
        language: response.response.language
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Si hay código, preguntar si ejecutarlo
      if (response.response.needs_code && response.response.code) {
        setCodeToExecute({
          code: response.response.code,
          language: response.response.language || 'python'
        });
      }

      // Si es una nueva conversación, notificar al componente padre
      if (!conversationId && response.conversation_id) {
        window.dispatchEvent(new CustomEvent('conversationCreated', { 
          detail: { conversationId: response.conversation_id } 
        }));
      }
    } catch (error) {
      console.error('Error enviando mensaje:', error);
      let errorText = 'Error al enviar el mensaje';
      
      if (error.response) {
        // Error del servidor
        errorText = error.response.data?.error || error.response.data?.message || errorText;
      } else if (error.request) {
        // Error de conexión
        errorText = 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.';
      } else {
        // Otro error
        errorText = error.message || errorText;
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `❌ ${errorText}`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteCode = async (code, language) => {
    try {
      const result = await executeScript(code, language);
      setCodeToExecute(null);
      
      // Agregar resultado como mensaje del sistema
      const resultMessage = {
        id: Date.now(),
        role: 'system',
        content: `Ejecución del script:\n\nSalida:\n${result.output || 'Sin salida'}\n${result.error ? `\nError:\n${result.error}` : ''}`,
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, resultMessage]);
    } catch (error) {
      console.error('Error ejecutando código:', error);
      alert(`Error ejecutando código: ${error.message}`);
    }
  };

  const handleCancelExecution = () => {
    setCodeToExecute(null);
  };

  if (!conversationId) {
    return (
      <div className="chat-area empty">
        <div className="empty-chat">
          <h2>Selecciona una conversación</h2>
          <p>O crea una nueva desde el panel izquierdo</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h2>Chat</h2>
        {username && <span className="username">Usuario: {username}</span>}
      </div>
      <MessageList messages={messages} loading={loading} />
      <div ref={messagesEndRef} />
      <MessageInput onSend={handleSendMessage} disabled={loading} />
      {codeToExecute && (
        <CodeExecutionModal
          code={codeToExecute.code}
          language={codeToExecute.language}
          onExecute={handleExecuteCode}
          onCancel={handleCancelExecution}
        />
      )}
    </div>
  );
}

export default ChatArea;

