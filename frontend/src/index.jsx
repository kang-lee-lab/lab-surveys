import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

// Auth0Provider lives in App, inside the router -- see
// auth/Auth0ProviderWithNavigate.jsx.
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
