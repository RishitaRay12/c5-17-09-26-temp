import React, { useState, type ChangeEvent, type FormEvent } from 'react';
import './UploadDocumentCard.css';
import { api, type UploadResponse } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const UploadDocumentCard: React.FC = () => {
  const { token } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [response, setResponse] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    if (!token) {
      setError('You must be signed in to upload a document.');
      return;
    }

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const data = await api.uploadDocument(file, token);
      setResponse(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred while uploading.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="swagger-post-card">
      <div 
        className="swagger-header" 
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="swagger-header-left">
          {/* <span className="swagger-method-badge">POST</span>
          <span className="swagger-endpoint-path">/upload-document</span> */}
          <span className="swagger-endpoint-summary">Upload And Index Document</span>
        </div>
        <span className="swagger-arrow">{isExpanded ? '▲' : '▼'}</span>
      </div>

      {isExpanded && (
        <div className="swagger-body">
          <form onSubmit={handleSubmit}>
            <div className="swagger-form-group">
              <label className="swagger-label">
                Select Document <span className="swagger-required">*</span>
              </label>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileChange}
                className="swagger-file-input"
              />
            </div>

            <div className="swagger-actions">
              <button 
                type="submit" 
                disabled={loading || !file} 
                className="swagger-submit-btn"
              >
                {loading ? 'Uploading...' : 'Execute'}
              </button>
            </div>
          </form>

          {error && (
            <div className="swagger-error-box">
              <strong>Error:</strong> {error}
            </div>
          )}

          {response && (
            <div className="swagger-response-box">
              <div className="swagger-response-title">Response Body</div>
              <pre className="swagger-code-block">
                {JSON.stringify(response, null, 2)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};