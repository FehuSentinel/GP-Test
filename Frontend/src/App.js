import React, { useState, useEffect } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import OnboardingModal from './components/OnboardingModal';
import { checkUsername, setUsername } from './services/api';

function App() {
  const [username, setUsernameState] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    // Verificar si hay nombre de usuario configurado
    checkUsername()
      .then(data => {
        if (data.username) {
          setUsernameState(data.username);
        } else {
          setShowOnboarding(true);
        }
      })
      .catch(error => {
        console.error('Error verificando usuario:', error);
        setShowOnboarding(true);
      });
  }, []);

  const handleUsernameSubmit = async (name) => {
    try {
      await setUsername(name);
      setUsernameState(name);
      setShowOnboarding(false);
    } catch (error) {
      console.error('Error estableciendo usuario:', error);
    }
  };

  return (
    <div className="app">
      {showOnboarding ? (
        <OnboardingModal onSubmit={handleUsernameSubmit} />
      ) : (
        <>
          <Sidebar 
            currentConversation={currentConversation}
            onSelectConversation={setCurrentConversation}
          />
          <ChatArea 
            conversationId={currentConversation}
            username={username}
          />
        </>
      )}
    </div>
  );
}

export default App;

