# Kang Lee Lab Surveys — Frontend

React UI for the Kang Lee Lab Surveys website. See the [repository root README](../README.md) for full monorepo setup.

## Running locally

```bash
npm install
cp .env.example .env
npm start
```

Opens http://localhost:3000

## Environment variables

See `.env.example`. `REACT_APP_AUTH0_AUDIENCE` must byte-match the backend's
`AUTH0_AUDIENCE`, or the API rejects every token as having the wrong audience.

## Authentication

Auth0 via `@auth0/auth0-react`.

| File | Role |
|------|------|
| `src/auth/Auth0ProviderWithNavigate.jsx` | Auth0 provider, rendered inside the router |
| `src/auth/useAccessToken.js` | access token: `null` for guests, a token, or throws if a signed-in session cannot be renewed |
| `src/api/client.js` | `useApi()` -- axios with the token attached when there is one |
| `src/contexts/AuthContext.jsx` | `useAuth()` -- `isAuthenticated`, `isLoading`, `isStaff`, `sub`, `email`, `login`, `logout` |

Guests send no `Authorization` header and keep full access to the demo surveys.

`/profile` ("My Surveys") lists the signed-in participant's responses from
`GET /surveys/participants/me/responses`. Surveys taken while signed out are not
saved.

Survey history and the CSV export need `isStaff`, which comes from
`GET /surveys/me`. To grant it, see
[backend/README.md](../backend/README.md#granting-staff-access).
