# Kang Lee Lab Surveys Architecture

This details the architecture of the kangleelabs-survey website.

## Tech-stack

1. Front-end: React, JavaScript, HTML, CSS
2. Back-end: Python, Django, SQL
3. Data layer: PostgreSQL
4. Tools: VSCode, pgAdmin, Google Cloud Run, Vercel, Supabase, Auth0

## Deployment in Production

Production runs on Google Cloud Run, Vercel and Supabase. Cloud Run hosts the
back-end as two services -- `legacy` and `modern`, which pin different
scikit-learn versions -- Vercel hosts the front-end, and Supabase holds the
production database.

That Supabase instance is shared with the `llm_psych_assessment` project, which
owns the `public` schema. This app's tables live in a `lab_surveys` schema and
are reached by a dedicated `lab_surveys_app` role with no privileges on
`public`. First-time setup is in [README.md](README.md#production-database-supabase).

## Authentication

We are using Auth0 for our authentication needs, this provides the API for us to securely login/logout and store user information. We currently do not support creating an account through our website, all accounts are manually created on Auth0 to control who has access to survey data.

### Maintenance/Gotchas

1. When deploying the backend, make sure every environment variable is set on
   **both** Cloud Run services. A variable added locally but not there is a
   common cause of bugs. Missing database variables no longer fail silently:
   `settings.py` refuses to boot when `K_SERVICE` is set and the database
   engine still resolves to sqlite.

2. Since we are using the free tier version of Supabase, it will deactivate our database after a certain amount of time if there is no activity. If we run into an issue submitting a survey or etc. try seeing if our database is inactivated on Supabase.

3. If we change the models, run the migration against Supabase too, so the
   production schema matches. Point `backend/.env` at Supabase, run
   `python manage.py migrate`, then restore your local `.env`. Migrations are
   run from a workstation, never from Cloud Run.
