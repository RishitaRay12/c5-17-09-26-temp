import React, { type ChangeEvent } from 'react';
import { Upload, FileText, Loader2, History, Plus } from 'lucide-react';
import { type ThreadItem } from '../services/api';

interface SidebarProps {
  file: File | null;
  uploading: boolean;
  threads: ThreadItem[];
  activeThreadId: string | null;
  onUpload: (e: ChangeEvent<HTMLInputElement>) => void;
  onCreateNewThread: () => void;
  onSelectThread: (threadId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  file,
  uploading,
  threads,
  activeThreadId,
  onUpload,
  onCreateNewThread,
  onSelectThread,
}) => {
  return (
    <aside className="w-80 border-r border-slate-800 p-6 flex flex-col gap-6 bg-slate-900/50">
      <div>
        <h2 className="text-xl font-bold bg-linear-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
          Vector Store RAG
        </h2>
        <p className="text-xs text-slate-400 mt-1">Upload PDF & Query Embeddings</p>
      </div>

      <div className="border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-5 text-center transition-all bg-slate-950/40">
        <input
          type="file"
          accept=".pdf"
          onChange={onUpload}
          className="hidden"
          id="pdf-upload"
          disabled={uploading}
        />
        <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center gap-2">
          {uploading ? (
            <Loader2 className="w-7 h-7 text-indigo-400 animate-spin" />
          ) : (
            <Upload className="w-7 h-7 text-indigo-400" />
          )}
          <span className="text-xs font-medium text-slate-300">
            {uploading ? 'Processing & Indexing...' : 'Upload PDF Document'}
          </span>
          <span className="text-[10px] text-slate-500">Extracts text & tables into ChromaDB</span>
        </label>
      </div>

      <button
        onClick={onCreateNewThread}
        className="flex items-center justify-center gap-2 py-2 px-4 bg-indigo-600/20 border border-indigo-500/40 text-indigo-300 text-xs font-medium rounded-lg hover:bg-indigo-600/30 transition-colors"
      >
        <Plus className="w-4 h-4" />
        <span>New Chat Session</span>
      </button>

      {file && (
        <div className="flex items-center gap-3 p-3 bg-slate-900 rounded-lg border border-slate-800">
          <FileText className="w-5 h-5 text-indigo-400 shrink-0" />
          <div className="overflow-hidden text-xs">
            <p className="font-medium text-slate-200 truncate">{file.name}</p>
            <p className="text-slate-500 font-mono mt-0.5">Active File</p>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-2 mt-2">
        <p className="text-xs font-semibold text-slate-400 flex items-center gap-1.5 mb-3">
          <History className="w-3.5 h-3.5" /> Recent Threads
        </p>
        {threads.map((item) => (
          <button
            key={item.thread_id}
            onClick={() => onSelectThread(item.thread_id)}
            className={`w-full text-left px-3 py-2.5 rounded-lg text-xs font-mono transition-colors truncate ${
              activeThreadId === item.thread_id
                ? 'bg-indigo-600/30 text-indigo-300 border border-indigo-500/30'
                : 'bg-slate-900/60 text-slate-400 hover:bg-slate-800'
            }`}
          >
            {item.title || `Thread: ${item.thread_id.slice(0, 12)}...`}
          </button>
        ))}
        {threads.length === 0 && (
          <p className="text-xs text-slate-500">No saved threads yet.</p>
        )}
      </div>
    </aside>
  );
};