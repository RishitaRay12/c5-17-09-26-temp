 
import React, { useEffect, useState } from 'react';
import remarkGfm from 'remark-gfm';
import ReactMarkdown from 'react-markdown';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Send, 
  ArrowLeft, 
  Bot, 
  User, 
  Loader2, 
  Database,
  Sparkles,
  AlertCircle,
  FileText,
  Zap,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { api } from '../services/api';
import '../pages/ThreadsView.css';

export interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  sources?: SourceMetadata[];
  tokenUsage?: TokenUsage;
}


export interface SourceMetadata {
  file_name?: string;
  document_name?: string;
  source?: string;
  page?: number | null;
  page_number?: number | null;
  content?: string;
  snippet?: string;
  [key: string]: any;
}

export interface TokenUsage {
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  [key: string]: any;
}


export const ChatView: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Thread ID from navigation state
  const navigationThreadId = (location.state as { activeThreadId?: string })?.activeThreadId;
  const [threadId, setThreadId] = useState<string | null>(navigationThreadId || null);

  // State Hooks
  const [input, setInput] = useState<string>(''); // Ensures 'input' is defined in scope
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [historyLoading, setHistoryLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (threadId) return;

    const token = localStorage.getItem('token');
    if (!token) {
      setError('Unauthorized access. Redirecting to login...');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
      return;
    }

    api.createThread(token)
      .then((thread) => setThreadId(thread.thread_id))
      .catch((err: unknown) => {
        console.error('Failed to create chat thread:', err);
        setError(err instanceof Error ? err.message : 'Could not initialize a chat thread.');
      });
  }, [navigate, threadId]);
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !threadId) {
      return;
    }

    setHistoryLoading(true);
    setError(null);

    api.getThreadHistory(threadId, token)
      .then((history) => {
        const historyArray = Array.isArray(history) ? history : [];
        const formattedMessages: Message[] = historyArray.map((item, index) => ({
          id: item.id || `history-${index}`,
          sender: item.role === 'user' ? 'user' : 'bot',
          text: item.content || '',
          sources: item.sources || [],
          tokenUsage: item.token_usage || undefined,
        }));
        setMessages(formattedMessages);
      })
      .catch((err: unknown) => {
        console.error('Failed to load thread history:', err);
        const errorMessage = err instanceof Error ? err.message : '';
        if (errorMessage.includes('Unauthorized')) {
          localStorage.removeItem('token');
          setError('Session expired. Please log in again.');
          setTimeout(() => navigate('/login', { replace: true }), 1500);
        } else {
          setError('Could not retrieve thread history.');
        }
      })
      .finally(() => setHistoryLoading(false));
  }, [threadId, navigate]);

  const toggleSources = (msgId: string) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const stripMarkdown = (text: string) => {
    return text
      .replaceAll('\\n', '\n') // Fix escaped newlines
      .replace(/[*_~`#]/g, '')  // Remove *, _, ~, `, and # symbols
      .replace(/\[(.*?)\]\(.*?\)/g, '$1'); // Convert links [text](url) to plain text
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const token = localStorage.getItem('token');
    if (!token) {
      setError('Session expired. Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
      return;
    }

    if (!input.trim() || loading || !threadId) return;

    const userMessageText = input.trim();
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: userMessageText,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const res = await api.chat(
        {
          thread_id: threadId,
          question: userMessageText,
        },
        token
      );

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: res.answer || 'No response content.',
        sources: res.sources || [],
        tokenUsage: res.token_usage || undefined,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: unknown) {
      console.error('Failed to send message:', err);
      const errorMessage = err instanceof Error ? err.message : '';
      if (errorMessage.includes('Unauthorized')) {
        setError('Session expired. Please log in again.');
        setTimeout(() => navigate('/login'), 1500);
      } else {
        setError('Failed to reach AI service.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="threads-container">
      <div className="threads-card chat-card">
        
        {/* Header */}
        <div className="chat-header">
          <button 
            onClick={() => navigate('/dashboard')} 
            className="chat-back-btn"
            title="Back to Threads"
          >
            <ArrowLeft className="btn-icon" />
          </button>

          <div className="chat-header-info">
            <div className="chat-header-title-row">
              <Database className="chat-header-icon" />
              <h1 className="threads-title chat-title">Thread Session</h1>
            </div>
            <p className="threads-subtitle font-mono">ID: {threadId}</p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="threads-error">
            <AlertCircle className="threads-error-icon" />
            <span>{error}</span>
          </div>
        )}

        {/* Messages */}
        <div className="chat-messages-container">
          {historyLoading ? (
            <div className="threads-empty-state">
              <Loader2 className="spinner-large" />
              <span className="loading-text">Loading conversation history...</span>
            </div>
          ) : messages.length === 0 ? (
            <div className="threads-empty-state">
              <div className="threads-badge">
                <Sparkles className="threads-badge-icon" />
              </div>
              <p className="empty-title">Thread Initialized</p>
              <p className="empty-subtitle">Start typing below to query vector store context.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div 
                key={msg.id} 
                className={`chat-bubble-wrapper ${msg.sender === 'user' ? 'chat-user' : 'chat-bot'}`}
              >
                <div className="chat-avatar">
                  {msg.sender === 'user' ? (
                    <User className="chat-avatar-icon" />
                  ) : (
                    <Bot className="chat-avatar-icon" />
                  )}
                </div>
                <div className="chat-bubble-content">
                  <p className="chat-bubble-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
          // Bold text styling (replaces double asterisks **)
          strong: ({ node, ...props }) => (
            <strong className="font-bold text-white" {...props} />
          ),
          // Heading level 2 (##)
          h2: ({ node, ...props }) => (
            <h2 className="text-base font-bold text-white mt-4 mb-2 border-b border-gray-700 pb-1" {...props} />
          ),
          // Heading level 3 (###)
          h3: ({ node, ...props }) => (
            <h3 className="text-sm font-bold text-blue-400 mt-3 mb-1" {...props} />
          ),
          // Paragraph spacing
          p: ({ node, ...props }) => (
            <p className="mb-2" {...props} />
          ),
          // Unordered lists (*)
          ul: ({ node, ...props }) => (
            <ul className="list-disc list-inside my-2 space-y-1 pl-2 text-gray-200" {...props} />
          ),
          // Ordered lists (1., 2.)
          ol: ({ node, ...props }) => (
            <ol className="list-decimal list-inside my-2 space-y-1 pl-2 text-gray-200" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="ml-1" {...props} />
          ),
          // Tables (requires remark-gfm)
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-3">
              <table className="min-w-full divide-y divide-gray-700 border border-gray-700 rounded text-xs" {...props} />
            </div>
          ),
          th: ({ node, ...props }) => (
            <th className="px-3 py-2 bg-gray-800 font-semibold text-left text-gray-200" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-3 py-2 border-t border-gray-800 text-gray-300" {...props} />
          )}}>{stripMarkdown(msg.text)}</ReactMarkdown>
                  </p>
                  {msg.sender === 'bot' && msg.sources && msg.sources.length > 0 && (
                    <div className="chat-sources-wrapper">
                      <button 
                        onClick={() => toggleSources(msg.id)} 
                        className="chat-sources-toggle"
                      >
                        <FileText className="meta-icon" />
                        <span>{msg.sources.length} Cited Source{msg.sources.length > 1 ? 's' : ''}</span>
                        {expandedSources[msg.id] ? (
                          <ChevronUp className="meta-icon-sm" />
                        ) : (
                          <ChevronDown className="meta-icon-sm" />
                        )}
                      </button>

                      {expandedSources[msg.id] && (
                        <div className="chat-sources-list">
                          {msg.sources.map((src, i) => (
                            <div key={i} className="chat-source-item">
                              <span className="source-name">
                                {src.file_name || src.document_name || src.source || `Document Chunk ${i + 1}`}
                              </span>
                              {(src.page || src.page_number) && <span className="source-page">Page {src.page || src.page_number}</span>}
                              {(src.content || src.snippet) && (
                                <p className="source-snippet">"{src.content || src.snippet}"</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Render Token Usage Metadata */}
                  {msg.sender === 'bot' && msg.tokenUsage && (
                    <div className="chat-meta-usage">
                      <Zap className="meta-icon-sm" />
                      <span>
                        Tokens: {msg.tokenUsage.total_tokens ??
                          msg.tokenUsage.usage?.total_tokens ??
                          ((msg.tokenUsage.prompt_tokens || msg.tokenUsage.usage?.prompt_tokens || 0) +
                           (msg.tokenUsage.completion_tokens || msg.tokenUsage.usage?.completion_tokens || 0))}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {loading && (
            <div className="chat-bubble-wrapper chat-bot">
              <div className="chat-avatar">
                <Bot className="chat-avatar-icon" />
              </div>
              <div className="chat-bubble-content loading-bubble">
                <Loader2 className="btn-spinner" />
                <span className="loading-text">Generating response...</span>
              </div>
            </div>
          )}
        </div>

        {/* Form Container */}
        <form onSubmit={handleSendMessage} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading || historyLoading}
            className="chat-input-field"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading || historyLoading}
            className="threads-btn-primary chat-send-btn"
          >
            {loading ? <Loader2 className="btn-spinner" /> : <Send className="btn-icon" />}
          </button>
        </form>

      </div>
    </div>
  );
};

