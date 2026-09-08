import React from "react";
import "./Header.css";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import logo from "../../assets/images/logos/lab-logo.webp";

function Header() {
  const { isAuthenticated, isLoading, isStaff, email, login, logout } = useAuth();

  return (
    <div className="header">
      <div className="header-left">
        <a
          href={"https://www.kangleelab.com/"}
          target="_blank"
          rel="noopener noreferrer"
        >
          <img className="logo" src={logo} alt="Lab Logo" />
        </a>
        <Link to={"/"}>Home</Link>
        <Link to={"/participate"}>Participate</Link>
      </div>
      <div className="header-right">
        {isAuthenticated ? (
          <div className="user-menu">
            <span className="user-email">
              {email}
              {isStaff && <span className="staff-badge"> (staff)</span>}
            </span>
            <button className="auth-button" onClick={logout}>
              Sign Out
            </button>
          </div>
        ) : (
          <button className="auth-button" onClick={login} disabled={isLoading}>
            Sign In
          </button>
        )}
      </div>
    </div>
  );
}

export default Header;
