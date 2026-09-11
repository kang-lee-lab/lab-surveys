import React from "react";
import { Auth0Provider } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";

/**
 * Auth0Provider wired to the router.
 *
 * This has to render *inside* <Router> so it can use useNavigate. redirect_uri
 * is an origin, so the page the user was on is always lost across the login
 * round trip; onRedirectCallback puts them back using appState.returnTo, which
 * every login call site passes.
 *
 * Navigation goes through the router rather than history.replaceState, which
 * would change the URL without telling the router and leave the rendered view
 * out of sync with it.
 */
function Auth0ProviderWithNavigate({ children }) {
  const navigate = useNavigate();

  return (
    <Auth0Provider
      domain={process.env.REACT_APP_AUTH0_DOMAIN}
      clientId={process.env.REACT_APP_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: window.location.origin,
        // Required. Without an audience Auth0 issues an opaque token that the
        // backend cannot validate, and every API call 401s while the user
        // appears perfectly signed in.
        audience: process.env.REACT_APP_AUTH0_AUDIENCE,
      }}
      onRedirectCallback={(appState) =>
        navigate(appState?.returnTo ?? "/", { replace: true })
      }
      cacheLocation="localstorage"
    >
      {children}
    </Auth0Provider>
  );
}

export default Auth0ProviderWithNavigate;
