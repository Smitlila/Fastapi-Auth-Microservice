# SecureAuthX

A minimal FastAPI JWT auth demo with access/refresh tokens, Postgres, and rate limiting.

## Stack
- FastAPI, Pydantic v2, SQLAlchemy 2.0
- JWT via PyJWT; password hashing via passlib/bcrypt
- Postgres 16 (Docker)
- Uvicorn

## Configuration
Env vars (see `.env.example`):
- `DATABASE_URL` (default: `postgresql+psycopg2://postgres:postgres@db:5432/secureauthx` in Docker)
- `JWT_SECRET` (change in non-dev)
- `ACCESS_TOKEN_TTL_MIN`, `REFRESH_TOKEN_TTL_DAYS`, `JWT_ISSUER`, `JWT_ALG`

Local/host testing DB URL (Docker mapped port):
```
postgresql+psycopg2://postgres:postgres@localhost:55432/secureauthx
```

## Run with Docker
```
cp .env.example .env
docker compose up --build
```
Services:
- API: http://localhost:8000
- Postgres: host port 55432 -> container 5432

## Run locally (without Docker)
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/secureauthx"
export JWT_SECRET="CHANGE_ME"
uvicorn app.main:app --reload
```

## Endpoints (high level)
- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET  /api/users/me` (requires bearer access token)
- `GET  /api/admin/dashboard` (requires admin bearer)
- `GET  /health`

## Tests
Using the Docker Postgres:
```
docker compose up -d
PYTHONPATH=$(pwd) \
DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:55432/secureauthx" \
JWT_SECRET="TEST_SECRET" \
pytest
```

## Notes
- Simple in-memory rate limiter; use Redis for production.
- Tables auto-created on startup for demo; use migrations (e.g., Alembic) for real deployments.
# Fastapi-Auth-Microservice
