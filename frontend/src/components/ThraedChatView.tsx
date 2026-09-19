// import React, { useState, useEffect } from 'react';
// import { useNavigate, useLocation } from 'react-router-dom';
// import { 
//   Send, 
//   ArrowLeft, 
//   Bot, 
//   User, 
//   Loader2, 
//   Database,
//   Sparkles,
//   AlertCircle
// } from 'lucide-react';
// import { api } from '../services/api';
// import '../pages/ThreadsView.css';

// interface Message {
//   id: string;
//   sender: 'user' | 'bot';
//   text: string;
// }

// export const ThreadChatView: React.FC = () => {
//   const navigate = useNavigate();
//   const location = useLocation();

//   const threadId = (location.state as { activeThreadId?: string })?.activeThreadId || 'new-session';

//   const [input, setInput] = useState<string>('');
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [loading, setLoading] = useState<boolean>(false);
//   const [historyLoading, setHistoryLoading] = useState<boolean>(true);
//   const [error, setError] = useState<string | null>(null);

//   // 1. Fetch Thread History on Component Mount
//   useEffect(() => {
//     const token = localStorage.getItem('access_token');
//     if (!token) {
//       setError('Unauthorized access. Redirecting to login...');
//       setTimeout(() => navigate('/login', { replace: true }), 1500);
//       return;
//     }

//     setHistoryLoading(true);
//     setError(null);

//     // Call thread history API endpoint
//     api.getThreadHistory(threadId, token)
//       .then((history) => {
//         // Map raw API message objects to state UI model
//         const formattedMessages: Message[] = (history || []).map(
//           (item: any, index: number) => ({
//             id: item.id || `history-${index}`,
//             sender: item.role === 'user' || item.sender === 'user' ? 'user' : 'bot',
//             text: item.content || item.question || item.answer || item.text || '',
//           })
//         );
//         setMessages(formattedMessages);
//       })
//       .catch((err: any) => {
//         console.error('Failed to load thread history:', err);
//         if (err.status === 401 || err.message?.includes('Unauthorized')) {
//           localStorage.removeItem('access_token');
//           setError('Session expired. Please log in again.');
//           setTimeout(() => navigate('/login', { replace: true }), 1500);
//         } else {
//           setError('Could not retrieve thread history.');
//         }
//       })
//       .finally(() => setHistoryLoading(false));
//   }, [threadId, navigate]);

//   // 2. Handle Sending New Messages
//   const handleSendMessage = async (e: React.FormEvent) => {
//     e.preventDefault();

//     const token = localStorage.getItem('access_token');
//     if (!token) {
//       setError('Session expired. Redirecting to login...');
//       setTimeout(() => navigate('/login', { replace: true }), 1500);
//       return;
//     }

//     if (!input.trim() || loading) return;

//     const userMessageText = input.trim();
//     const userMsg: Message = {
//       id: Date.now().toString(),
//       sender: 'user',
//       text: userMessageText,
//     };

//     setMessages((prev) => [...prev, userMsg]);
//     setInput('');
//     setLoading(true);
//     setError(null);

//     try {
//       const res = await api.chat(
//         {
//           thread_id: threadId,
//           question: userMessageText,
//         },
//         token
//       );

//       const botMsg: Message = {
//         id: (Date.now() + 1).toString(),
//         sender: 'bot',
//         text: res.answer || 'No response content.',
//       };
//       setMessages((prev) => [...prev, botMsg]);
//     } catch (err: any) {
//       console.error('Failed to send message:', err);
//       if (err.status === 401 || err.message?.includes('Unauthorized')) {
//         localStorage.removeItem('access_token');
//         setError('Unauthorized session. Please log in again.');
//         setTimeout(() => navigate('/login', { replace: true }), 1500);
//       } else {
//         setError('Failed to reach AI service.');
//       }
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="threads-container">
//       <div className="threads-card chat-card">
        
//         {/* Header */}
//         <div className="chat-header">
//           <button 
//             onClick={() => navigate('/dashboard')} 
//             className="chat-back-btn"
//             title="Back to Threads"
//           >
//             <ArrowLeft className="btn-icon" />
//           </button>

//           <div className="chat-header-info">
//             <div className="chat-header-title-row">
//               <Database className="chat-header-icon" />
//               <h1 className="threads-title chat-title">Thread Session</h1>
//             </div>
//             <p className="threads-subtitle font-mono">ID: {threadId}</p>
//           </div>
//         </div>

//         {/* Error Display */}
//         {error && (
//           <div className="threads-error">
//             <AlertCircle className="threads-error-icon" />
//             <span>{error}</span>
//           </div>
//         )}

//         {/* Messages / Loading Area */}
//         <div className="chat-messages-container">
//           {historyLoading ? (
//             <div className="threads-empty-state">
//               <Loader2 className="spinner-large" />
//               <span className="loading-text">Loading conversation history...</span>
//             </div>
//           ) : messages.length === 0 ? (
//             <div className="threads-empty-state">
//               <div className="threads-badge">
//                 <Sparkles className="threads-badge-icon" />
//               </div>
//               <p className="empty-title">Thread Initialized</p>
//               <p className="empty-subtitle">Start typing below to query vector store context.</p>
//             </div>
//           ) : (
//             messages.map((msg) => (
//               <div 
//                 key={msg.id} 
//                 className={`chat-bubble-wrapper ${msg.sender === 'user' ? 'chat-user' : 'chat-bot'}`}
//               >
//                 <div className="chat-avatar">
//                   {msg.sender === 'user' ? (
//                     <User className="chat-avatar-icon" />
//                   ) : (
//                     <Bot className="chat-avatar-icon" />
//                   )}
//                 </div>
//                 <div className="chat-bubble-content">
//                   <p className="chat-bubble-text">{msg.text}</p>
//                 </div>
//               </div>
//             ))
//           )}

//           {loading && (
//             <div className="chat-bubble-wrapper chat-bot">
//               <div className="chat-avatar">
//                 <Bot className="chat-avatar-icon" />
//               </div>
//               <div className="chat-bubble-content loading-bubble">
//                 <Loader2 className="btn-spinner" />
//                 <span className="loading-text">Generating response...</span>
//               </div>
//             </div>
//           )}
//         </div>

//         {/* Form Input */}
//         <form onSubmit={handleSendMessage} className="chat-input-form">
//           <input
//             type="text"
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             placeholder="Type your message..."
//             disabled={loading || historyLoading}
//             className="chat-input-field"
//           />
//           <button
//             type="submit"
//             disabled={!input.trim() || loading || historyLoading}
//             className="threads-btn-primary chat-send-btn"
//           >
//             {loading ? <Loader2 className="btn-spinner" /> : <Send className="btn-icon" />}
//           </button>
//         </form>

//       </div>
//     </div>
//   );
// };
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
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
import { useAuth } from '../context/AuthContext';
import '../pages/ThreadsView.css';

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

export interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  sources?: SourceMetadata[];
  tokenUsage?: TokenUsage;
}

export const ThreadChatView: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { threadId: routeThreadId } = useParams<{ threadId: string }>();
  const { token } = useAuth();

  const threadId = routeThreadId ||
    (location.state as { activeThreadId?: string })?.activeThreadId ||
    'new-session';

  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [historyLoading, setHistoryLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  // Fetch History on Mount
  useEffect(() => {
    if (!token) {
      setError('Unauthorized access. Redirecting to login...');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
      return;
    }

    setHistoryLoading(true);
    setError(null);

    api.getThreadHistory(threadId, token)
      .then((history) => {
        const historyArray = Array.isArray(history) ? history :  [];
        const formattedMessages: Message[] = historyArray.map((item: any, index: number) => ({
          id: item.id || `history-${index}`,
          sender: item.role === 'user' || item.sender === 'user' ? 'user' : 'bot',
          text: item.content || item.answer || item.question || item.text || '',
          sources: item.sources || [],
          tokenUsage: item.token_usage || undefined
        }));
        setMessages(formattedMessages);
      })
      .catch((err: any) => {
        console.error('Failed to load thread history:', err);
        if (err.status === 401 || err.message?.includes('Unauthorized')) {
            localStorage.removeItem('token');
          setError('Session expired. Please log in again.');
          setTimeout(() => navigate('/login', { replace: true }), 1500);
        } else {
          setError('Could not retrieve thread history.');
        }
      })
      .finally(() => setHistoryLoading(false));
  }, [threadId, navigate, token]);

  const toggleSources = (msgId: string) => {
    setExpandedSources((prev) => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    const accessToken = token || localStorage.getItem('token');
    if (!accessToken) {
      setError('Session expired. Redirecting to login...');
      setTimeout(() => navigate('/login', { replace: true }), 1500);
      return;
    }

    if (!input.trim() || loading) return;

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
        accessToken
      );

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: res.answer || 'No answer returned.',
        sources: res.sources || [],
        tokenUsage: res.token_usage || undefined,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      console.error('Failed to send message:', err);
      if (err.status === 401 || err.message?.includes('Unauthorized')) {
        localStorage.removeItem('token');
        setError('Unauthorized session. Please log in again.');
        setTimeout(() => navigate('/login', { replace: true }), 1500);
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

        {/* Messages Container */}
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
                  <p className="chat-bubble-text"><ReactMarkdown>{msg.text}</ReactMarkdown></p>

                  {/* Render Sources metadata for Bot messages */}
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
                          ((msg.tokenUsage.prompt_tokens || 0) + (msg.tokenUsage.completion_tokens || 0))}
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
                <span className="loading-text">Searching vector embeddings & generating response...</span>
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSendMessage} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question..."
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



