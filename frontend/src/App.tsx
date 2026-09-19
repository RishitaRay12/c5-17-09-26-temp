// import {
//   BrowserRouter,
//   Routes,
//   Route,
// } from "react-router-dom";

// import { AuthProvider } from "./context/AuthContext";

// // import ProtectedRoute from "./components/ProtectedRoute";
// // import AppLayout from "./components/AppLayout";

// import Login from "./pages/auth/Login";
// import Register from "./pages/auth/Register";
// import AppLayout from "./components/AppLayout";
// import ProtectedRoute from "./components/ProtectedRoute";
// // import Dashboard from "./pages/Dashboard";
// import { DocumentChatView } from "./components/DocumentChatView";


// // import Dashboard from "./pages/Dashboard";
// // import NewProject from "./pages/NewProject";
// // import Project from "./pages/Project";

// function App() {
//   return (
//     <AuthProvider>

//       <BrowserRouter>

//         <Routes>

//           {/* ================================
//               Public
//           ================================= */}

//           <Route
//             path="/login"
//             element={<Login />}
//           />

//           <Route
//             path="/register"
//             element={<Register />}
//           />

//           <Route
//             path="*"
//             element={<Login />}
//           />
           
//           {/* ================================
//               Protected
//           ================================= */}

//           <Route element={<ProtectedRoute />}>

// {/* Shared Sidebar Layout */}
//           <Route element={<AppLayout />}>
//           <Route
//                 path="/abc"
//                 element={<DocumentChatView />}
//               />
//           </Route>
//           </Route>

//         </Routes>

//       </BrowserRouter>

//     </AuthProvider>
//   );
// }

// export default App;


import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import  ProtectedRoute from './components/ProtectedRoute';
import  AppLayout  from './components/AppLayout';
import  Login  from './pages/auth/Login';
import Register  from './pages/auth/Register';
import { ThreadsView } from './pages/ThreadsView';
import { ChatView } from './components/ChatView';
import { ThreadChatView } from './components/ThraedChatView';
import { UploadDocumentCard } from './components/UploadDocumentCard';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              {/* Main Document Vector Search App */}
              <Route path="/dashboard" element={<ThreadsView />} />
              <Route path="/new" element={<ChatView />} />
              <Route path="/history/:threadId" element={<ThreadChatView />} />
              <Route path="/upload" element={<UploadDocumentCard />} />
              {/* <Route path="/abc" element={<DocumentChatView />} /> */}
            </Route>
          </Route>

          {/* Fallback Catch-All */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;