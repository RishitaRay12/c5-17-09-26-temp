// import React, { useState, useEffect, type ChangeEvent, type FormEvent } from 'react';
// import { Loader2, Bot } from 'lucide-react';
// import { api } from '../services/api';
// import { type ChatMessage, type ThreadItem } from '../services/api';
// import { useAuth } from '../context/AuthContext';
// import { Sidebar } from './Sidebar';
// import { ChatMessageItem } from './ChatMessageItem';
// // import { ChatInput } from './ChatView';

// export const DocumentChatView: React.FC = () => {
//   const { token } = useAuth();
//   const authToken = token || '';

//   const [file, setFile] = useState<File | null>(null);
//   const [uploading, setUploading] = useState<boolean>(false);
//   const [threads, setThreads] = useState<ThreadItem[]>([]);
//   const [threadId, setThreadId] = useState<string | null>(null);
//   const [messages, setMessages] = useState<ChatMessage[]>([]);
//   const [input, setInput] = useState<string>('');
//   const [loading, setLoading] = useState<boolean>(false);
//   const [fetchingHistory, setFetchingHistory] = useState<boolean>(false);

//   useEffect(() => {
//     if (!authToken) return;
//     api.listThreads(authToken)
//       .then((data) => setThreads(data))
//       .catch((err) => console.error('Failed to load threads:', err));
//   }, [authToken]);

//   useEffect(() => {
//     if (!threadId || !authToken) return;

//     setFetchingHistory(true);
//     api.getThreadHistory(threadId, authToken)
//       .then((history) => setMessages(history))
//       .catch((err) => console.error('Failed to fetch history:', err))
//       .finally(() => setFetchingHistory(false));
//   }, [threadId, authToken]);

//   const handleCreateNewThread = async (): Promise<void> => {
//     try {
//       const res = await api.createThread(authToken);
//       setThreadId(res.thread_id);
//       setMessages([]);
//       setFile(null);
//       setThreads((prev) => [
//         { thread_id: res.thread_id, title: 'New chat' },
//         ...prev,
//       ]);
//     } catch (err) {
//       console.error('Failed to create thread:', err);
//     }
//   };

//   const handleUpload = async (e: ChangeEvent<HTMLInputElement>): Promise<void> => {
//     const selectedFile = e.target.files?.[0];
//     if (!selectedFile) return;

//     setUploading(true);
//     try {
//       await api.uploadDocument(selectedFile, authToken);
//       const threadRes = await api.createThread(authToken);
//       setThreadId(threadRes.thread_id);
//       setFile(selectedFile);
//       setMessages([]);
//       setThreads((prev) => [
//         { thread_id: threadRes.thread_id, title: selectedFile.name },
//         ...prev,
//       ]);
//     } catch (err) {
//       console.error('Document processing failed:', err);
//     } finally {
//       setUploading(false);
//     }
//   };

//   const handleSend = async (e: FormEvent<HTMLFormElement>): Promise<void> => {
//     e.preventDefault();
//     if (!input.trim() || !threadId) return;

//     const userMessage = input.trim();
//     setInput('');
//     setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
//     setLoading(true);

//     try {
//       const res = await api.chat({ thread_id: threadId, question: userMessage }, authToken);
//       setMessages((prev) => [
//         ...prev,
//         {
//           role: 'assistant',
//           content: res.answer,
//           sources: res.sources,
//         },
//       ]);
//     } catch (err) {
//       console.error('Failed to send message:', err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="flex h-screen bg-slate-950 text-slate-100 font-sans">
//       <Sidebar
//         file={file}
//         uploading={uploading}
//         threads={threads}
//         activeThreadId={threadId}
//         onUpload={handleUpload}
//         onCreateNewThread={handleCreateNewThread}
//         onSelectThread={setThreadId}
//       />

//       <main className="flex-1 flex flex-col">
//         <div className="flex-1 overflow-y-auto p-6 space-y-4">
//           {fetchingHistory ? (
//             <div className="flex items-center justify-center h-full text-slate-500 text-sm gap-2">
//               <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
//               <span>Fetching history...</span>
//             </div>
//           ) : messages.length === 0 ? (
//             <div className="flex flex-col items-center justify-center h-full text-slate-500 text-sm gap-2">
//               <Bot className="w-10 h-10 text-slate-700" />
//               <p>Upload a PDF or select a thread to start chatting.</p>
//             </div>
//           ) : (
//             messages.map((msg, idx) => <ChatMessageItem key={idx} message={msg} />)
//           )}

//           {loading && (
//             <div className="flex items-center gap-2 text-slate-400 text-sm">
//               <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
//               <span>Searching ChromaDB embeddings...</span>
//             </div>
//           )}
//         </div>

//         <form onSubmit={handleSend} className="flex gap-2 border-t border-slate-800 p-4">
//           <input
//             value={input}
//             onChange={(e) => setInput(e.target.value)}
//             disabled={!threadId || loading}
//             placeholder="Ask a question about your document..."
//             className="flex-1 rounded border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100"
//           />
//           <button
//             type="submit"
//             disabled={!threadId || !input.trim() || loading}
//             className="rounded bg-indigo-500 px-4 py-2 text-white disabled:opacity-50"
//           >
//             Send
//           </button>
//         </form>
//       </main>
//     </div>
//   );
// };