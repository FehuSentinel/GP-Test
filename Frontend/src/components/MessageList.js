import React from 'react';
import './MessageList.css';
import Message from './Message';

function MessageList({ messages, loading }) {
  return (
    <div className="message-list">
      {messages.length === 0 && !loading ? (
        <div className="empty-messages">
          <p>No hay mensajes aún</p>
          <p className="hint">Comienza una conversación escribiendo un mensaje</p>
        </div>
      ) : (
        messages.map(message => (
          <Message key={message.id} message={message} />
        ))
      )}
      {loading && (
        <div className="loading-message">
          <div className="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}
    </div>
  );
}

export default MessageList;

