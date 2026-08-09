import React from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import "./DashboardLayout.css";

function DashboardLayout() {
  const navigate = useNavigate();

  const user = JSON.parse(
    localStorage.getItem("currentUser")
  );

  const handleLogout = () => {
    localStorage.removeItem("currentUser");
    navigate("/");
  };

  return (
    <div className="dashboard-layout">

      <aside className="sidebar">

        <div className="sidebar-logo">
          <div className="sidebar-symbol">✦</div>
          <span>CosmeticConflict</span>
        </div>

        <nav className="sidebar-nav">

          <NavLink
            to="/dashboard"
            end
            className={({ isActive }) =>
              isActive ? "side-link active" : "side-link"
            }
          >
            🏠 Dashboard
          </NavLink>

          <NavLink
            to="/dashboard/analyze"
            className={({ isActive }) =>
              isActive ? "side-link active" : "side-link"
            }
          >
            🔍 Analyze
          </NavLink>

          <NavLink
            to="/dashboard/results"
            className={({ isActive }) =>
              isActive ? "side-link active" : "side-link"
            }
          >
            📊 Results
          </NavLink>

          <NavLink
            to="/dashboard/history"
            className={({ isActive }) =>
              isActive ? "side-link active" : "side-link"
            }
          >
            🕘 History
          </NavLink>

          <NavLink
            to="/dashboard/profile"
            className={({ isActive }) =>
              isActive ? "side-link active" : "side-link"
            }
          >
            👤 Profile
          </NavLink>

        </nav>

        <button
          className="logout-button"
          onClick={handleLogout}
        >
          ↪ Logout
        </button>

      </aside>

      <main className="dashboard-main">

        <header className="dashboard-header">

          <div>
            <h2>CosmeticConflict</h2>
            <span>Cosmetic Ingredient Analysis</span>
          </div>

          <div className="header-user">

            <div className="user-avatar">
              {user?.name?.charAt(0).toUpperCase()}
            </div>

            <div>
              <strong>{user?.name}</strong>
              <small>{user?.email}</small>
            </div>

          </div>

        </header>

        <div className="dashboard-content">
          <Outlet />
        </div>

      </main>

    </div>
  );
}

export default DashboardLayout;