import { useCallback } from "react";
import axios from "axios";
import { useAccessToken } from "../auth/useAccessToken";

export const API_BASE = process.env.REACT_APP_API_ADDRESS;

/** The API rejected the credential (missing, expired or invalid). */
export class UnauthorizedError extends Error {
  constructor(message = "You need to sign in to do that.") {
    super(message);
    this.name = "UnauthorizedError";
  }
}

/** Signed in, but this account lacks the permission the route requires. */
export class ForbiddenError extends Error {
  constructor(message = "This account does not have access to that data.") {
    super(message);
    this.name = "ForbiddenError";
  }
}

/**
 * axios wrapper that attaches the Auth0 access token when there is one.
 *
 * Guests send no Authorization header at all: an empty "Bearer " is an
 * *invalid* credential rather than an absent one, and the API correctly
 * answers it with a 401 instead of treating the caller as anonymous.
 */
export function useApi() {
  const { getAccessToken } = useAccessToken();

  const request = useCallback(
    async (config) => {
      const token = await getAccessToken();
      const headers = { ...(config.headers ?? {}) };
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }

      try {
        return await axios({ ...config, headers });
      } catch (error) {
        const status = error?.response?.status;
        if (status === 401) throw new UnauthorizedError();
        if (status === 403) throw new ForbiddenError();
        throw error;
      }
    },
    [getAccessToken]
  );

  return { request };
}
