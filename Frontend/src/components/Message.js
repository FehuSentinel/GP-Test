import React from 'react';
import './Message.css';

function Message({ message }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  // Detectar bloques de código en el contenido
  const formatContent = (content) => {
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Agregar texto antes del bloque de código
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.substring(lastIndex, match.index)
        });
      }

      // Agregar bloque de código
      parts.push({
        type: 'code',
        language: match[1] || 'text',
        content: match[2]
      });

      lastIndex = match.index + match[0].length;
    }

    // Agregar texto restante
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.substring(lastIndex)
      });
    }

    if (parts.length === 0) {
      parts.push({ type: 'text', content });
    }

    return parts;
  };

  const formattedContent = formatContent(message.content);

  return (
    <div className={`message ${isUser ? 'user' : isSystem ? 'system' : 'assistant'}`}>
      <div className="message-content">
        {formattedContent.map((part, index) => {
          if (part.type === 'code') {
            return (
              <pre key={index} className="code-block">
                <code className={`language-${part.language}`}>{part.content}</code>
              </pre>
            );
          } else {
            return (
              <div key={index} className="text-content">
                {part.content.split('\n').map((line, lineIndex) => (
                  <React.Fragment key={lineIndex}>
                    {line}
                    {lineIndex < part.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
                ))}
              </div>
            );
          }
        })}
      </div>
    </div>
  );
}

export default Message;

