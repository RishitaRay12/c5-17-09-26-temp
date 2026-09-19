import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  MessageSquare, 
  Plus, 
  ArrowRight, 
  Loader2, 
  Database, 
  AlertCircle,
  Trash2
} from 'lucide-react';
import { api, type ThreadItem } from '../services/api';
import './ThreadsView.css';

export const ThreadsView: React.FC = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const authToken = token || '';

  const [threads, setThreads] = useState<ThreadItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [creating, setCreating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authToken) {
      setError('Authentication token missing. Please log in.');
      setLoading(false);
      return;
    }

    setLoading(true);
    api.listThreads(authToken)
      .then((data) => setThreads(data))
      .catch((err) => {
        console.error('Error fetching threads:', err);
        setError('Failed to load active threads. Please try again.');
      })
      .finally(() => setLoading(false));
  }, [authToken]);

  const handleCreateThread = async () => {
    setCreating(true);
    setError(null);
    try {
      const res = await api.createThread(authToken);
      navigate('/new', { state: { activeThreadId: res.thread_id } });
    } catch (err) {
      console.error('Failed to create thread:', err);
      setError('Could not initialize a new session.');
    } finally {
      setCreating(false);
    }
  };

  const handleSelectThread = (threadId: string) => {
    navigate(`/history/${threadId}`, { state: { activeThreadId: threadId } });
  };

  const handleDeleteThread = async (threadId: string) => {
    if (!window.confirm('Delete this thread and all of its chats?')) return;

    setError(null);
    try {
      await api.deleteThread(threadId, authToken);
      setThreads((current) => current.filter((thread) => thread.thread_id !== threadId));
    } catch (err) {
      console.error('Failed to delete thread:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete thread.');
    }
  };

  return (
    <div className="threads-container">
      <div className="threads-card">
        
        {/* Header */}
        <div className="threads-header">
          <div className="threads-badge">
            <Database className="threads-badge-icon" />
          </div>
          <h1 className="threads-title">
            Your Vector Threads
          </h1>
          <p className="threads-subtitle">
            Select an active vector thread or launch a new workspace
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="threads-error">
            <AlertCircle className="threads-error-icon" />
            <span>{error}</span>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleCreateThread}
          disabled={creating || loading}
          className="threads-btn-primary"
        >
          {creating ? (
            <Loader2 className="btn-spinner" />
          ) : (
            <Plus className="btn-icon" />
          )}
          <span>Create New Thread</span>
        </button>

        {/* Divider */}
        <div className="threads-divider">
          <div className="divider-line" />
          <span className="divider-text">
            Active Sessions ({threads.length})
          </span>
          <div className="divider-line" />
        </div>

        {/* Thread Item List */}
        <div className="threads-list">
          {loading ? (
            <div className="threads-empty-state">
              <Loader2 className="spinner-large" />
              <span className="loading-text">Fetching active threads...</span>
            </div>
          ) : threads.length === 0 ? (
            <div className="threads-empty-card">
              <MessageSquare className="empty-icon" />
              <p className="empty-title">No threads found.</p>
              <p className="empty-subtitle">Click above to start your first session.</p>
            </div>
          ) : (
            threads.map((item) => (
              <div
                key={item.thread_id}
                onClick={() => handleSelectThread(item.thread_id)}
                className="thread-item-card"
              >
                <div className="thread-item-content">
                  <div className="thread-icon-wrapper">
                    <MessageSquare className="thread-icon" />
                  </div>
                  <div className="thread-details">
                    <p className="thread-id-text">
                      Thread: {item.thread_id}
                    </p>
                    {item.last_updated && (
                      <p className="thread-date-text">
                        {new Date(item.last_updated).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>

                <div className="thread-actions">
                  <button
                    type="button"
                    className="thread-delete-btn"
                    title="Delete thread"
                    aria-label={`Delete thread ${item.thread_id}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      void handleDeleteThread(item.thread_id);
                    }}
                  >
                    <Trash2 className="thread-delete-icon" />
                  </button>
                  <ArrowRight className="thread-arrow-icon" onClick={() => handleSelectThread(item.thread_id)} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};