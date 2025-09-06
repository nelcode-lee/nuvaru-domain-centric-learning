import React, { useState, useRef, useEffect } from 'react';
import styles from './ChatInterface.module.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/learning/chat?query=${encodeURIComponent(userMessage.text)}&user_id=1`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: data.response || 'Sorry, I could not process your request.',
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: 'Sorry, there was an error processing your request. Please try again.',
          isUser: false,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I\'m having trouble connecting. Please check your connection and try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h2 className={styles.title}>AI Chat Interface</h2>
        <p className={styles.subtitle}>
          Ask questions about your uploaded documents
        </p>
        {messages.length > 0 && (
          <button onClick={clearChat} className={styles.clearButton}>
            Clear Chat
          </button>
        )}
      </div>
      
      <div className={styles.chatContainer}>
        <div className={styles.messagesContainer}>
          {messages.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>🤖</div>
              <h3 className={styles.emptyTitle}>Start a conversation</h3>
              <p className={styles.emptySubtitle}>
                Ask me anything about your uploaded documents
              </p>
              <div className={styles.suggestions}>
                <button 
                  className={styles.suggestionButton}
                  onClick={() => setInputText("What documents do I have?")}
                >
                  What documents do I have?
                </button>
                <button 
                  className={styles.suggestionButton}
                  onClick={() => setInputText("Summarize my knowledge base")}
                >
                  Summarize my knowledge base
                </button>
                <button 
                  className={styles.suggestionButton}
                  onClick={() => setInputText("What can you help me with?")}
                >
                  What can you help me with?
                </button>
              </div>
            </div>
          ) : (
            <div className={styles.messages}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`${styles.message} ${message.isUser ? styles.userMessage : styles.aiMessage}`}
                >
                  <div className={styles.messageAvatar}>
                    {message.isUser ? '👤' : '🤖'}
                  </div>
                  <div className={styles.messageContent}>
                    <div className={styles.messageText}>{message.text}</div>
                    <div className={styles.messageTime}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className={`${styles.message} ${styles.aiMessage}`}>
                  <div className={styles.messageAvatar}>🤖</div>
                  <div className={styles.messageContent}>
                    <div className={styles.typingIndicator}>
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
        
        <div className={styles.inputContainer}>
          <div className={styles.inputWrapper}>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your documents..."
              className={styles.messageInput}
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputText.trim() || isLoading}
              className={styles.sendButton}
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;