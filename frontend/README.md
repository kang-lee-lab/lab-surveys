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

See `.env.example`. Generate an admin password hash:

```bash
node scripts/generate-password-hash.js yourpassword
```

## Admin authentication

Authenticated admins can view survey history and export CSV data. Sessions expire after 24 hours and are stored in localStorage.
