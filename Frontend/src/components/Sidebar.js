import React, { useState, useEffect } from 'react';
import './Sidebar.css';
import { getConversations, createConversation, deleteConversation } from '../services/api';

function Sidebar({ currentConversation, onSelectConversation, user, onLogout }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
      setLoading(false);
    } catch (error) {
      console.error('Error cargando conversaciones:', error);
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await createConversation();
      await loadConversations();
      onSelectConversation(newConv.id);
    } catch (error) {
      console.error('Error creando conversación:', error);
    }
  };

  const handleDeleteConversation = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteConversation(id);
      await loadConversations();
      if (currentConversation === id) {
        onSelectConversation(null);
      }
    } catch (error) {
      console.error('Error eliminando conversación:', error);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>GP-Test</h2>
        <button className="new-chat-btn" onClick={handleNewConversation}>
          + Nueva conversación
        </button>
      </div>
      {user && (
        <div className="user-info">
          <div className="user-details">
            <span className="user-name">{user.username}</span>
            <span className="user-email">{user.email}</span>
          </div>
          <button className="logout-btn" onClick={onLogout} title="Cerrar sesión">
            🚪
          </button>
        </div>
      )}
      <div className="conversations-list">
        {loading ? (
          <div className="loading">Cargando...</div>
        ) : conversations.length === 0 ? (
          <div className="empty-state">
            <p>No hay conversaciones</p>
            <p className="hint">Crea una nueva para comenzar</p>
          </div>
        ) : (
          conversations.map(conv => (
            <div
              key={conv.id}
              className={`conversation-item ${currentConversation === conv.id ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <span className="conversation-title">{conv.title || `Conversación ${conv.id}`}</span>
              <button
                className="delete-btn"
                onClick={(e) => handleDeleteConversation(conv.id, e)}
                title="Eliminar conversación"
              >
                ×
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Sidebar;

