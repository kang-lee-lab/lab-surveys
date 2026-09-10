# Kang Lee Lab Surveys

Computational survey tools for the Kang Lee Development Lab. The current stack is a React frontend and Django backend with PostgreSQL. Survey results are computed dynamically, including machine learning models where applicable.

| Directory | Description |
|-----------|-------------|
| `frontend/` | React UI (Create React App) |
| `backend/` | Django API, survey definitions, ML models |

## Quickstart

Prerequisites: Docker Desktop, Node 18+.

```bash
# 1. Database, migrations and both backends (from the repository root)
cp backend/.env.example backend/.env
docker compose up --build -d

# 2. Frontend
cd frontend
npm install
cp .env.example .env
npm start
```

Open **http://localhost:3000**.

Both `.env.example` files are pre-filled for local development, Auth0 dev tenant
included, so nothing needs editing to get started.

First build takes several minutes; afterwards `docker compose up -d` is seconds.

Check the backends are up:

```bash
curl http://127.0.0.1:8000/surveys/wakeup   # {"status": "awake"}
curl http://127.0.0.1:8001/surveys/wakeup   # {"status": "awake"}
```

Stop with `docker compose down`, or `docker compose down -v` to discard the
database too.

### What is running

| Service | Address | Notes |
|---------|---------|-------|
| frontend | http://localhost:3000 | the app |
| `legacy_backend` | http://127.0.0.1:8000 | sklearn 1.0.2 — ASQ, DASS, MMPI, NAFLD, Child BMI |
| `modern_backend` | http://127.0.0.1:8001 | sklearn 1.4.2 — DASS Multiclass Anxiety |
| `postgres` | `localhost:5434` | database `lab_surveys`, user/password `postgres` |
| `migrate` | — | one-shot; applies migrations before the backends start |

**ASQ, DASS, MMPI, NAFLD and Child BMI only work in Docker** — their models
need scikit-learn 1.0.2, and `requirements.txt` pins 1.4.2, so a native server
returns a 500 for them.

Postgres data lives in the `postgres_data` volume and survives
`docker compose down`. Development does not use Supabase; production points
`DB_*` at its own managed database.

Schema and API tiers: [backend/README.md](backend/README.md#database).

### If something does not start

| Symptom | Fix |
|---------|-----|
| `Bind for 0.0.0.0:5434 failed: port is already allocated` | another stack holds the port; change the `postgres` host port in `docker-compose.yml` and `DB_PORT` in `backend/.env` |
| `Something is already running on port 3000` | an old `npm start` is still alive; stop it |
| Build fails on a pip read timeout | rerun `docker compose build`; it resumes from the layer cache |
| History or CSV export returns 403 while signed in | Auth0 RBAC is not enabled — see [backend/README.md](backend/README.md#granting-staff-access) |

### Backend (native, without Docker)

For the tests and the surveys needing no legacy model:

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
docker compose up -d postgres    # or set DB_* at a database of your own
python manage.py migrate
python manage.py runserver
```

`DEBUG` is hardcoded to `False` in `backend/labsurveysbackend/settings.py` so that deployments never expose stack traces. For local debugging, set it to `True` temporarily — but revert it before committing.

## Environment variables

- **Frontend** — `frontend/.env.example`
- **Backend** — `backend/.env.example`

Never commit `.env` files.

`AUTH0_AUDIENCE` and `REACT_APP_AUTH0_AUDIENCE` must be identical.

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
