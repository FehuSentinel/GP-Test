import React from 'react';
import './CodeExecutionModal.css';

function CodeExecutionModal({ code, language, onExecute, onCancel }) {
  return (
    <div className="code-modal-overlay">
      <div className="code-modal">
        <h3>¿Ejecutar este código?</h3>
        <div className="code-preview">
          <div className="code-header">
            <span className="language-badge">{language || 'text'}</span>
          </div>
          <pre className="code-content">
            <code>{code}</code>
          </pre>
        </div>
        <div className="code-modal-actions">
          <button className="cancel-btn" onClick={onCancel}>
            Cancelar
          </button>
          <button className="execute-btn" onClick={() => onExecute(code, language)}>
            Ejecutar
          </button>
        </div>
      </div>
    </div>
  );
}

export default CodeExecutionModal;

