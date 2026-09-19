import type { TokenUsage } from "../components/ChatView";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export interface UserRegister {
  username: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SourceMetadata {
  source?: string;
  snippet?: string;
  page?: number | null;
  document_name?: string;
  page_number?: number | null;
}

export interface ChatRequest {
  thread_id: string;
  question: string;
}

export interface ChatResponse {
  answer: string;
  sources?: SourceMetadata[];
  token_usage?: TokenUsage;
}

export interface ThreadIdResponse {
  thread_id: string;
}

export interface UploadResponse {
  message?: string;
  filename?: string;
  status?: string;
  files_processed?: number;
  documents_added?: number;
}

export interface ThreadItem {
  thread_id: string;
  title: string;
  last_updated?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceMetadata[];
  id?: string;
  token_usage?: TokenUsage;
}

export const api = {
  // Auth
  register: async (data: UserRegister): Promise<void> => {
    const res = await fetch(`${API_BASE_URL}/users/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Registration failed');
  },

  login: async (formData: FormData): Promise<TokenResponse> => {
    const res = await fetch(`${API_BASE_URL}/users/login`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Login failed');
    return res.json();
  },

  // Document & Vector Search
  uploadDocument: async (file: File, token: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('single_file', file);
    const res = await fetch(`${API_BASE_URL}/upload-document`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => null) as { detail?: string } | null;
      throw new Error(body?.detail || `Upload failed (${res.status})`);
    }
    return res.json();
  },

  createThread: async (token: string): Promise<ThreadIdResponse> => {
    const res = await fetch(`${API_BASE_URL}/create_threads`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to create thread');
    return res.json();
  },

  deleteThread: async (threadId: string, token: string): Promise<void> => {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/threads/${threadId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      throw new Error(`Cannot reach the backend at ${API_BASE_URL}. Start the API server or check CORS.`);
    }
    if (!res.ok) {
      const body = await res.json().catch(() => null) as { detail?: string } | null;
      throw new Error(body?.detail || `Failed to delete thread (${res.status})`);
    }
  },

  chat: async (payload: ChatRequest, token: string): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => null) as { detail?: string } | null;
      const error = new Error(body?.detail || `Chat request failed (${res.status})`);
      Object.assign(error, { status: res.status });
      throw error;
    }
    return res.json();
  },

  listThreads: async (token: string): Promise<ThreadItem[]> => {
    const res = await fetch(`${API_BASE_URL}/threads`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch threads');
    return res.json();
  },
  // Add to api object in src/services/api.ts
getThreadHistory: async (threadId: string, token: string): Promise<ChatMessage[]> => {
    const res = await fetch(`${API_BASE_URL}/threads/${threadId}/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to fetch thread history');

    const data = await res.json();
    return (data.messages || []).map((message: {
        id?: string;
        role: ChatMessage['role'];
        message?: string;
        content?: string;
        sources?: SourceMetadata[];
        token_usage?: TokenUsage;
      }) => ({
        id: message.id,
        role: message.role,
        content: message.content || message.message || '',
        sources: message.sources || [],
        token_usage: message.token_usage,
      }));
  },
};