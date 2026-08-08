# Kang Lee Lab Surveys

Computational survey tools for the Kang Lee Development Lab. The current stack is a React frontend and Django backend with PostgreSQL. Survey results are computed dynamically, including machine learning models where applicable.

| Directory | Description |
|-----------|-------------|
| `frontend/` | React UI (Create React App) |
| `backend/` | Django API, survey definitions, ML models |

## Running locally

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # then edit as needed
npm start              # http://localhost:3000
```

### Backend (single server)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # then edit as needed
python manage.py runserver
```

The frontend expects the legacy API at `http://127.0.0.1:8000` by default.

### Backend (dual ML environments via Docker)

Some surveys require sklearn 1.0.2 (legacy) and DASS multiclass requires sklearn 1.4.2 (modern). From the repository root:

```bash
docker compose up
```

- Legacy backend: http://127.0.0.1:8000
- Modern backend (DASS multiclass): http://127.0.0.1:8001

Configure `frontend/.env` accordingly (see `frontend/.env.example`).

## Environment variables

- **Frontend** — `frontend/.env.example`
- **Backend** — `backend/.env.example`

Never commit `.env` files.

## Development

The `main` branch is protected; changes should come through pull requests.

Branch naming: `<yourname>/<issue_ID>/<brief-description>`

- Backend CI runs on changes to `backend/**`
- Frontend CI runs on changes to `frontend/**`

Install pre-commit at the repo root: `pre-commit install`

## Roadmap

See [docs/implementation-plan.md](docs/implementation-plan.md) for the phased plan (catalog-driven UI, data collection, Auth0 profiles, metadata-driven results).

## Adding a new survey

See [backend/README.md](backend/README.md) for the full guide (homepage card, JSON survey files, views, results page).

## Deployment

Production uses separate hosts for frontend and backend (Heroku, Vercel, Supabase). When deploying from this monorepo:

- **Backend (Heroku)** — set the app root / build context to `backend/`
- **Frontend (Vercel or Heroku)** — set the root directory to `frontend/`

See [backend/ARCHITECTURE.md](backend/ARCHITECTURE.md) for architecture and operational notes.

## License

See [LICENSE](LICENSE).
