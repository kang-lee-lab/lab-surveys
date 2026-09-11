import React, { createContext, useContext, useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { API_BASE, useApi } from "../api/client";

const AuthContext = createContext(null);

/** The Auth0 permission that marks a lab staff account. */
export const STAFF_PERMISSION = "read:responses";

const GUEST = { sub: null, email: null, permissions: [] };

/**
 * Session state for the whole app, derived from Auth0.
 *
 * Staff status comes from GET /surveys/me rather than from anything decoded in
 * the browser, so the backend stays the single authority on who is staff. This
 * flag only decides what the UI offers -- the API enforces the permission on
 * every staff route regardless of what the client believes.
 */
export function AuthProvider({ children }) {
  const {
    isAuthenticated,
    isLoading: isAuth0Loading,
    loginWithRedirect,
    logout: auth0Logout,
  } = useAuth0();
  const { request } = useApi();

  const [profile, setProfile] = useState(GUEST);
  const [isProfileLoading, setIsProfileLoading] = useState(false);

  useEffect(() => {
    // The SDK reports signed-out until it finishes restoring the session, so
    // acting on isAuthenticated before that resets state on every page load --
    // including immediately after the login redirect.
    if (isAuth0Loading) return;

    if (!isAuthenticated) {
      setProfile(GUEST);
      setIsProfileLoading(false);
      return;
    }

    let cancelled = false;
    setIsProfileLoading(true);

    request({ method: "get", url: `${API_BASE}/me` })
      .then((response) => {
        if (cancelled) return;
        setProfile({
          sub: response.data.sub,
          email: response.data.email,
          permissions: response.data.permissions ?? [],
        });
      })
      .catch((error) => {
        if (cancelled) return;
        // Signed in with a token the API will not accept. Treat it as no
        // privileges rather than guessing, and leave the error visible.
        console.error("Could not load the signed-in profile:", error);
        setProfile(GUEST);
      })
      .finally(() => {
        if (!cancelled) setIsProfileLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [isAuthenticated, isAuth0Loading, request]);

  const login = () =>
    // redirect_uri is an origin, so without returnTo every login drops the
    // user on the homepage instead of the page they were reading.
    loginWithRedirect({ appState: { returnTo: window.location.pathname } });

  const logout = () =>
    auth0Logout({ logoutParams: { returnTo: window.location.origin } });

  const value = {
    isAuthenticated,
    isLoading: isAuth0Loading || isProfileLoading,
    isStaff: profile.permissions.includes(STAFF_PERMISSION),
    sub: profile.sub,
    email: profile.email,
    permissions: profile.permissions,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
