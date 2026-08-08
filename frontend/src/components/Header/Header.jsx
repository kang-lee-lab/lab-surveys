import React, { useState } from "react";
import "./Header.css";
import { Link } from "react-router-dom";
import { useAuth0 } from "@auth0/auth0-react";
import { useAuth } from "../../contexts/AuthContext";
import LoginModal from "../LoginModal/LoginModal";
import logo from "../../assets/images/logos/lab-logo.webp";

function Header() {
  const { isAuthenticated: isAdminAuthenticated, logout: adminLogout } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  const {
    isAuthenticated: isUserAuthenticated,
    user,
    loginWithRedirect,
    logout: auth0Logout,
  } = useAuth0();

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
        {!isAdminAuthenticated && (
          <button className="admin-toggle" onClick={() => setIsLoginModalOpen(true)}>
            Log In
          </button>
        )}
        {isAdminAuthenticated && (
          <button className="admin-toggle" onClick={adminLogout}>
            Log Out
          </button>
        )}
      </div>
      <div className="header-right">
        {isUserAuthenticated ? (
          <div className="user-menu">
            <span className="user-email">{user?.email}</span>
            <button
              className="auth-button"
              onClick={() =>
                auth0Logout({ logoutParams: { returnTo: window.location.origin } })
              }
            >
              Sign Out
            </button>
          </div>
        ) : (
          <button className="auth-button" onClick={() => loginWithRedirect()}>
            Sign In
          </button>
        )}
      </div>
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />
    </div>
  );
}

export default Header;
