import React, { useState } from 'react';
import './LoginModal.css';

function LanguageSelector({ onSelectLanguage, username }) {
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedLanguage) {
      setError('Por favor selecciona un idioma');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await onSelectLanguage(selectedLanguage);
    } catch (err) {
      setError(err.message || 'Error al establecer el idioma');
      setLoading(false);
    }
  };

  return (
    <div className="login-overlay">
      <div className="login-modal">
        <h1>GP-Test</h1>
        <h2>¡Bienvenido{username ? `, ${username}` : ''}!</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '25px' }}>
          Selecciona el idioma en el que quieres que la IA te responda
        </p>
        <form onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '20px' }}>
            <label 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '15px',
                background: selectedLanguage === 'es' ? 'rgba(74, 144, 226, 0.1)' : 'var(--bg-primary)',
                border: `2px solid ${selectedLanguage === 'es' ? 'var(--accent-primary)' : 'var(--accent-secondary)'}`,
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => setSelectedLanguage('es')}
            >
              <input
                type="radio"
                name="language"
                value="es"
                checked={selectedLanguage === 'es'}
                onChange={() => setSelectedLanguage('es')}
                style={{ marginRight: '12px', width: '20px', height: '20px', cursor: 'pointer' }}
                disabled={loading}
              />
              <div>
                <strong style={{ color: 'var(--accent-primary)', fontSize: '16px' }}>Español (Latinoamericano)</strong>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: '5px 0 0 0' }}>
                  La IA responderá completamente en español
                </p>
              </div>
            </label>
            
            <label 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                padding: '15px',
                background: selectedLanguage === 'en' ? 'rgba(74, 144, 226, 0.1)' : 'var(--bg-primary)',
                border: `2px solid ${selectedLanguage === 'en' ? 'var(--accent-primary)' : 'var(--accent-secondary)'}`,
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.3s ease'
              }}
              onClick={() => setSelectedLanguage('en')}
            >
              <input
                type="radio"
                name="language"
                value="en"
                checked={selectedLanguage === 'en'}
                onChange={() => setSelectedLanguage('en')}
                style={{ marginRight: '12px', width: '20px', height: '20px', cursor: 'pointer' }}
                disabled={loading}
              />
              <div>
                <strong style={{ color: 'var(--accent-primary)', fontSize: '16px' }}>English</strong>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px', margin: '5px 0 0 0' }}>
                  The AI will respond completely in English
                </p>
              </div>
            </label>
          </div>
          <button type="submit" className="login-button" disabled={loading || !selectedLanguage}>
            {loading ? 'Guardando...' : 'Continuar'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LanguageSelector;

