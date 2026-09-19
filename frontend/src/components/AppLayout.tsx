import {
  Outlet,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import "./AppLayout.css";

function AppLayout() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const username = user?.username || "Account";
  const handleLogout = () => {
    logout();
    navigate("/login", {
      replace: true,
    });
  };

  return (
      <div className="app-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="logo">
            🚀
            <div>
              <strong>Financial Decision and</strong>
              <br />
              <strong>Intelligence Support System</strong>
            </div>
          </div>
  
          <nav className="sidebar-nav">
            <button className="menu-item active" onClick={() => navigate("/dashboard")}>
              Dashboard
            </button>
  
            {/* <button className="menu-item">My Projects</button> */}
  
            <button
              className="menu-item"
              onClick={() => navigate("/upload")}
            >
              Upload PDF
            </button>
  
            {/* <button className="menu-item">Chatbot</button>
  
            <button className="menu-item">Evaluate</button>
  
            <button className="menu-item">Results / Reports</button> */}
          </nav>
  
          <div className="sidebar-bottom">
            <button className="menu-item">{username}</button>
  
            <button
              className="menu-item logout-item"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </aside>
  
        <main className="layout-content">
          <Outlet />
        </main>
       
      </div>
    );
  //   <div className="dashboard-page">
  //     {/* Sidebar */}
  //     <aside className="sidebar">
  //       <div className="logo">
  //         🚀
  //         <div>
  //           <strong>AI Startup</strong>
  //           <br />
  //           <strong>Co-Founder</strong>
  //         </div>
  //       </div>

  //       <nav className="sidebar-nav">
  //         <button className="menu-item active">Dashboard</button>

  //         <button className="menu-item">My Projects</button>

  //         <button
  //           className="menu-item"
  //           onClick={() => navigate("/new-project")}
  //         >
  //           New Project
  //         </button>

  //         <button className="menu-item">Chatbot</button>

  //         <button className="menu-item">Evaluate</button>

  //         <button className="menu-item">Results / Reports</button>
  //       </nav>

  //       <div className="sidebar-bottom">
  //         <button className="menu-item">Settings</button>

  //         <button
  //           className="menu-item logout-item"
  //           onClick={handleLogout}
  //         >
  //           Logout
  //         </button>
  //       </div>
  //     </aside>

  //     {/* Main Content */}
     
  //   </div>
  // );
}


export default AppLayout;