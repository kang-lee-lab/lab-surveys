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

Sign-in goes through Auth0 (`@auth0/auth0-react`). The pieces:

| File | Role |
|------|------|
| `src/auth/Auth0ProviderWithNavigate.jsx` | the provider, rendered inside the router so the login redirect can return the user to the page they were on |
| `src/auth/useAccessToken.js` | the access token in three states: `null` for guests, a token, or a throw when a signed-in session cannot be renewed |
| `src/api/client.js` | `useApi()` -- axios with the token attached when there is one |
| `src/contexts/AuthContext.jsx` | `useAuth()` -- session state, including `isStaff` |

Guests keep full access to the demo surveys and send no `Authorization` header
at all, because an empty `Bearer ` is an invalid credential rather than an
absent one.

### Pages

`/profile` ("My Surveys") lists the responses attributed to the
signed-in participant, from `GET /surveys/participants/me/responses`.
Surveys taken while signed out are not saved to any account.

### Staff access

Survey history and the CSV export are staff-only. `isStaff` comes from
`GET /surveys/me`, which reports the permissions Auth0 issued for the account --
the browser never decides this for itself, and the API enforces it regardless.
Granting a staff account is dashboard work: see
[backend/README.md](../backend/README.md#api-authentication).
