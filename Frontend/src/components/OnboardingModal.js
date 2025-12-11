import React, { useState } from 'react';
import './OnboardingModal.css';

function OnboardingModal({ onSubmit }) {
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim()) {
      onSubmit(username.trim());
    }
  };

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-modal">
        <h1>Bienvenido</h1>
        <p>Para comenzar, por favor ingresa tu nombre:</p>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Tu nombre"
            className="username-input"
            autoFocus
          />
          <button type="submit" className="submit-button" disabled={!username.trim()}>
            Continuar
          </button>
        </form>
      </div>
    </div>
  );
}

export default OnboardingModal;

