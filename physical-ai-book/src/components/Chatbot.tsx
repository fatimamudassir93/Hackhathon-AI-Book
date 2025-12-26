import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ChatbotFilters from './ChatbotFilters';
import styles from './Chatbot.module.css';

interface Source {
  chapter: string;
  title: string;
  section?: string;
  score: number;
  url?: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string | object;  // Allow content to be string or object for error handling
  sources?: Source[];
  citations?: string;
  in_scope?: boolean;
  error?: boolean;
}

interface ChatbotProps {
  apiUrl?: string;
}

const Chatbot: React.FC<ChatbotProps> = ({ apiUrl = 'http://localhost:8000' }) => {
  console.log('Chatbot: API_URL', apiUrl);
  const { token, user, isLoading: authLoading } = useAuth();
  console.log('Chatbot: token', token);
  console.log('Chatbot: user', user);
  console.log('Chatbot: authLoading', authLoading);

  
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [chapterFilter, setChapterFilter] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Listen for text selection
  useEffect(() => {
    // Only run in browser environment
    if (typeof window === 'undefined') return;

    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();
      if (text && text.length > 10) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const queryRAG = async (userQuery: string, useSelectedText: boolean = false): Promise<any> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    // Add auth token if available
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${apiUrl}/api/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: userQuery,
        selected_text: useSelectedText ? selectedText : undefined,
        chapter_filter: chapterFilter,
        use_history: true
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    // Validate the response structure
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid response format from server');
    }

    return data;
  };

  const handleSend = async (useSelectedText: boolean = false) => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Query the RAG backend with new enhanced endpoint
      const ragResults = await queryRAG(input, useSelectedText);

      // Create response with answer and sources from new API format
      const assistantMessage: Message = {
        role: 'assistant',
        content: typeof ragResults?.response === 'string' ? ragResults.response : 'No answer available.',
        sources: Array.isArray(ragResults?.sources) ? ragResults.sources : [],
        citations: typeof ragResults?.citations === 'string' ? ragResults.citations : '',
        in_scope: typeof ragResults?.in_scope === 'boolean' ? ragResults.in_scope : true,
        error: false
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Clear selected text after using it
      if (useSelectedText) {
        setSelectedText('');
      }
    } catch (error) {
      console.error('Error querying RAG:', error);

      // Determine error message based on error type
      let errorContent = 'Sorry, I encountered an error while searching the textbook.';

      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
          errorContent = '🔌 Cannot connect to the backend server. Please make sure it\'s running at ' + apiUrl;
        } else if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          errorContent = '🔒 Authentication required. Please sign in to use the chatbot.';
        } else if (error.message.includes('403') || error.message.includes('Forbidden')) {
          errorContent = '🚫 Access denied. You may not have permission to use this feature.';
        } else if (error.message.includes('500')) {
          errorContent = '⚠️ Server error. The backend encountered an issue. Please try again later.';
        } else {
          errorContent = `❌ Error: ${error.message}`;
        }
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: errorContent,
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          className={styles.chatButton}
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          💬
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <h3>📚 Ask about the Book</h3>
            <div className={styles.headerActions}>
              <ChatbotFilters
                apiUrl={apiUrl}
                selectedChapter={chapterFilter}
                onChapterChange={setChapterFilter}
              />
              <button
                className={styles.closeButton}
                onClick={() => setIsOpen(false)}
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className={styles.messagesContainer}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <p>👋 Hi! I can help you understand the Physical AI & Humanoid Robotics textbook.</p>
                <p>Ask me anything about:</p>
                <ul>
                  <li>Physical AI concepts</li>
                  <li>Embodied intelligence</li>
                  <li>ROS 2 and robotics frameworks</li>
                  <li>VSLAM and Navigation</li>
                  <li>Simulation environments</li>
                </ul>
                {selectedText && (
                  <div className={styles.selectedTextHint}>
                    💡 You have text selected. Click "Ask about Selection" to query it!
                  </div>
                )}
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.message} ${styles[msg.role]} ${msg.error ? styles.error : ''}`}
              >
                <div className={styles.messageContent}>
                  {typeof msg.content === 'string'
                    ? msg.content
                    : JSON.stringify(msg.content, null, 2) || 'No content available'}
                </div>
                {msg.in_scope === false && (
                  <div className={styles.outOfScopeNote}>
                    ℹ️ This question appears to be outside the textbook's scope.
                  </div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className={styles.sources}>
                    <strong>📖 Sources:</strong>
                    <ul>
                      {msg.sources.map((source, i) => (
                        <li key={i}>
                          <span className={styles.sourceChapter}>{source.chapter}</span>
                          {source.section && (
                            <> - <span className={styles.sourceSection}>{source.section}</span></>
                          )}
                          <div className={styles.sourceTitle}>{source.title}</div>
                          <span className={styles.sourceScore}>
                            (relevance: {(source.score * 100).toFixed(0)}%)
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {msg.citations && (
                  <div className={styles.citations}>
                    <details>
                      <summary>View Citations</summary>
                      <pre>{msg.citations}</pre>
                    </details>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.loadingDots}>
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className={styles.inputArea}>
            {selectedText && (
              <div className={styles.selectedTextBadge}>
                ✂️ Text selected ({selectedText.length} chars)
                <button onClick={() => setSelectedText('')}>✕</button>
              </div>
            )}
            <div className={styles.inputRow}>
              <textarea
                className={styles.input}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question about the book..."
                rows={2}
                disabled={isLoading}
              />
              <div className={styles.buttonGroup}>
                <button
                  className={styles.sendButton}
                  onClick={() => handleSend(false)}
                  disabled={isLoading || !input.trim()}
                  title="Ask about whole book"
                >
                  📚 Ask
                </button>
                {selectedText && (
                  <button
                    className={`${styles.sendButton} ${styles.selectionButton}`}
                    onClick={() => handleSend(true)}
                    disabled={isLoading || !input.trim()}
                    title="Ask about selected text"
                  >
                    ✂️ Ask Selection
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;
