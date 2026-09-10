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

### Backend and database (Docker — the normal path)

```bash
cp backend/.env.example backend/.env   # then edit as needed
docker compose up --build
```

That starts everything development needs:

| Service | Address | Notes |
|---------|---------|-------|
| `postgres` | `localhost:5434` | local dev database (`lab_surveys`, `postgres`/`postgres`) |
| `migrate` | — | one-shot; applies migrations, then the backends start |
| `legacy_backend` | http://127.0.0.1:8000 | sklearn 1.0.2 — ASQ, DASS, MMPI, NAFLD, Child BMI |
| `modern_backend` | http://127.0.0.1:8001 | sklearn 1.4.2 — DASS Multiclass Anxiety |

**Most surveys only work in Docker.** Their models were pickled under
scikit-learn 1.0.2 and cannot be unpickled by the 1.4.2 in `requirements.txt` --
a native server answers `POST /surveys/results` with a 500 for those surveys.
The two images exist precisely because the two sets of models need different
scikit-learn versions.

Host port 5434 avoids clashing with a native Postgres on 5432 and with the
llm_psych_assessment stack on 5433. Data lives in the
`postgres_data` volume and survives `docker compose down`; add `-v` to discard it.

Development does not use Supabase. Production points `DB_*` at its own managed
database.

### Backend (native, without Docker)

Useful for the tests and for the surveys that need no legacy model:

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

The Auth0 audience must be identical on both sides (`AUTH0_AUDIENCE` and
`REACT_APP_AUTH0_AUDIENCE`). See [backend/README.md](backend/README.md#api-authentication) for
the endpoint authentication tiers and how staff access is granted.

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
