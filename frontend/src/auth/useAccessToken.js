import { useCallback } from "react";
import { useAuth0 } from "@auth0/auth0-react";

/** Signed in, but the session could not be renewed. Prompt a fresh login. */
export class LoginRequiredError extends Error {
  constructor(message = "Your session expired. Please sign in again.") {
    super(message);
    this.name = "LoginRequiredError";
  }
}

/**
 * Access token in three states, not two:
 *
 *   signed out         -> null    (a guest; not an error)
 *   signed in, ok      -> token
 *   signed in, broken  -> throws  (expired session; prompt re-login)
 *
 * Never collapse the last two into null. A user whose session broke would keep
 * using the app, still see their name in the header, and silently stop having
 * anything attributed to their account.
 */
export function useAccessToken() {
  const { getAccessTokenSilently, isAuthenticated, isLoading } = useAuth0();

  const getAccessToken = useCallback(async () => {
    if (!isAuthenticated) return null;
    try {
      return await getAccessTokenSilently();
    } catch (error) {
      throw new LoginRequiredError();
    }
  }, [getAccessTokenSilently, isAuthenticated]);

  return { getAccessToken, isAuthenticated, isLoading };
}
