// import React from 'react';
// import { Bot, User, FileText } from 'lucide-react';
// import { type ChatMessage } from '../services/api';

// interface ChatMessageItemProps {
//   message: ChatMessage;
// }

// export const ChatMessageItem: React.FC<ChatMessageItemProps> = ({ message }) => {
//   const isUser = message.role === 'user';

//   return (
//     <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
//       {!isUser && (
//         <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
//           <Bot className="w-4 h-4" />
//         </div>
//       )}
//       <div
//         className={`max-w-2xl rounded-2xl p-4 text-sm leading-relaxed ${
//           isUser
//             ? 'bg-indigo-600 text-white rounded-tr-none'
//             : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'
//         }`}
//       >
//         <p>{message.content}</p>

//         {message.sources && message.sources.length > 0 && (
//           <div className="mt-3 pt-3 border-t border-slate-800/80 text-xs text-slate-400 space-y-1">
//             <span className="font-semibold text-indigo-400">Sources:</span>
//             {message.sources.map((src, i) => (
//               <div key={i} className="flex items-center gap-2">
//                 <FileText className="w-3 h-3 text-slate-500" />
//                 <span>
//                   {src.document_name || src.source || 'Unknown source'}
//                   {(src.page_number || src.page) && (
//                     <span className="text-slate-300"> — Page {src.page_number || src.page}</span>
//                   )}
//                 </span>
//                 {src.snippet && <span className="block text-slate-500">{src.snippet}</span>}
//               </div>
//             ))}
//           </div>
//         )}
//       </div>
//       {isUser && (
//         <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300 shrink-0">
//           <User className="w-4 h-4" />
//         </div>
//       )}
//     </div>
//   );
// };