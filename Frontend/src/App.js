import React, { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import LoginModal from './components/LoginModal';
import RegisterModal from './components/RegisterModal';
import LanguageSelector from './components/LanguageSelector';
import { login, register, isAuthenticated, getStoredUser, logout, getCurrentUser, setLanguage } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showLanguageSelector, setShowLanguageSelector] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar si hay usuario autenticado
    const checkAuth = async () => {
      if (isAuthenticated()) {
        try {
          // Verificar que el token sigue siendo válido
          const userData = await getCurrentUser();
          setUser(userData);
          // Si no tiene idioma configurado, mostrar selector
          if (!userData.language || userData.needs_language) {
            setShowLanguageSelector(true);
          }
        } catch (error) {
          // Token inválido, limpiar y mostrar login
          logout();
          setShowLogin(true);
        }
      } else {
        setShowLogin(true);
      }
      setLoading(false);
    };

    checkAuth();

    // Escuchar eventos de creación de conversación
    const handleConversationCreated = (event) => {
      setCurrentConversation(event.detail.conversationId);
    };

    window.addEventListener('conversationCreated', handleConversationCreated);
    
    return () => {
      window.removeEventListener('conversationCreated', handleConversationCreated);
    };
  }, []);

  const handleLogin = async (email, password) => {
    const response = await login(email, password);
    setUser(response.user);
    setShowLogin(false);
    setShowRegister(false);
    // Si necesita seleccionar idioma, mostrar selector
    if (response.needs_language || !response.user.language) {
      setShowLanguageSelector(true);
    }
  };

  const handleRegister = async (username, email, password) => {
    const response = await register(username, email, password);
    setUser(response.user);
    setShowLogin(false);
    setShowRegister(false);
    // Después del registro, siempre mostrar selector de idioma
    setShowLanguageSelector(true);
  };

  const handleLanguageSelect = async (language) => {
    await setLanguage(language);
    // Actualizar usuario con el idioma seleccionado
    const updatedUser = { ...user, language };
    setUser(updatedUser);
    setShowLanguageSelector(false);
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setCurrentConversation(null);
    setShowLogin(true);
  };

  if (loading) {
    return (
      <div className="app">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'var(--text-primary)' }}>
          Cargando...
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {showLanguageSelector && user ? (
        <LanguageSelector 
          onSelectLanguage={handleLanguageSelect}
          username={user.username}
        />
      ) : showLogin && !user ? (
        <LoginModal 
          onLogin={handleLogin}
          onSwitchToRegister={() => {
            setShowLogin(false);
            setShowRegister(true);
          }}
        />
      ) : showRegister && !user ? (
        <RegisterModal 
          onRegister={handleRegister}
          onSwitchToLogin={() => {
            setShowRegister(false);
            setShowLogin(true);
          }}
        />
      ) : user && !showLanguageSelector ? (
        <>
          <Sidebar 
            currentConversation={currentConversation}
            onSelectConversation={setCurrentConversation}
            user={user}
            onLogout={handleLogout}
          />
          <ChatArea 
            conversationId={currentConversation}
            username={user.username}
          />
        </>
      ) : null}
    </div>
  );
}

export default App;

