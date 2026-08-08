# Legacy Flask application

This is the original Kang Lee Lab Surveys implementation: Python + Flask with server-rendered HTML templates and PostgreSQL.

Production historically ran on Heroku at https://kangleelab-surveys.herokuapp.com/

The current application lives in `frontend/` (React) and `backend/` (Django). This directory is kept for reference and optional local runs of the old stack.

## Running locally

1. Set up PostgreSQL and create a `responses` table matching the `Response` model in `App/__init__.py`.
2. Copy `.env.example` to `.env` and configure the database URL.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python run.py`

See the root repository README for the modern stack.
