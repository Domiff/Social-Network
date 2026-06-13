# Social Network API

A social network backend built with FastAPI, featuring stateless JWT authentication (RS256) with access/refresh token rotation.

## Tech Stack

| Layer            | Technology                                      |
| ---------------- | ----------------------------------------------- |
| Runtime          | Python 3.14+, [uv](https://docs.astral.sh/uv/)  |
| Web framework    | FastAPI + Pydantic Settings                     |
| Database         | PostgreSQL (production) / SQLite (local)        |
| ORM & migrations | SQLAlchemy 2 (async), Alembic                   |
| Authentication   | PyJWT (RS256), pwdlib (argon2)                  |
| Logging          | structlog (structured JSON logs)                |
| Code quality     | ruff, pre-commit                                |

## Project Layout

```
src/
├── auth/              # Authentication domain
│   ├── router.py      #   /auth/* endpoints
│   ├── service.py     #   business logic
│   ├── repository.py  #   data access layer
│   ├── jwt.py         #   token issuing & validation
│   ├── depends.py     #   get_current_user dependency
│   └── models.py      #   User model
└── core/              # Application core
    ├── config.py      #   settings (env-driven)
    ├── database.py    #   async engine & session
    ├── logging.py     #   structlog configuration
    └── setup.py       #   app factory, middleware, healthcheck
migrations/            # Alembic migrations
keys/                  # RSA key pair for JWT signing (never commit)
```

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- OpenSSL (key generation)
- PostgreSQL 15+ (production mode)

### 1. Install dependencies

```bash
uv sync
```

### 2. Generate the JWT signing key pair

Tokens are signed with RS256. Generate a key pair and keep the private key secret:

```bash
mkdir -p keys
openssl genrsa -out keys/jwt-private.pem 2048
openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem
```

> In production, provision keys through your secret manager and mount them read-only. Rotate them periodically — rotation invalidates all outstanding tokens.

### 3. Configure the environment

Copy the template and adjust the values (or export variables via your orchestrator):

```bash
cp .env.template .env
```

```env
# Application
IS_DEBUG=false
IS_DOCKERIZED=true

# CORS
ALLOW_CREDENTIALS=true
ALLOW_ORIGINS=["https://app.example.com"]
ALLOW_METHODS=["GET","POST","PUT","PATCH","DELETE"]

# PostgreSQL (used when IS_DOCKERIZED=true)
POSTGRES_DB=social_network
POSTGRES_USER=social_network
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Configuration reference:

| Variable            | Default      | Description                                              |
| ------------------- | ------------ | -------------------------------------------------------- |
| `IS_DEBUG`          | `true`       | Enables OpenAPI docs; disable in production              |
| `IS_DOCKERIZED`     | `false`      | `true` → PostgreSQL, `false` → local SQLite (`db.sqlite3`) |
| `ALLOW_CREDENTIALS` | — (required) | CORS: allow cookies/credentials                          |
| `ALLOW_ORIGINS`     | — (required) | CORS: allowed origins (JSON list)                        |
| `ALLOW_METHODS`     | — (required) | CORS: allowed HTTP methods (JSON list)                   |
| `POSTGRES_*`        | see config   | PostgreSQL connection parameters                         |

Token lifetimes and key paths are defined in `src/core/config.py` (`AuthSettings`).

### 4. Apply migrations

```bash
uv run alembic upgrade head
```

### 5. Run

Development (auto-reload):

```bash
uv run fastapi dev src/main.py
```

Production (behind a reverse proxy terminating TLS):

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Interactive API docs are available at `/docs` only when `IS_DEBUG=true`.

## API Overview

| Method | Path             | Description                                          |
| ------ | ---------------- | ---------------------------------------------------- |
| POST   | `/auth/register` | Create an account → access token + refresh cookie    |
| POST   | `/auth/login`    | Authenticate with email/password                     |
| POST   | `/auth/refresh`  | Rotate the token pair using the refresh cookie       |
| POST   | `/auth/logout`   | Clear the refresh cookie                             |
| GET    | `/health`        | Liveness check (verifies database connectivity)      |

### Authentication model

- The **access token** is returned in the response body and must be sent as `Authorization: Bearer <token>`.
- The **refresh token** is stored in an `httponly`, `secure`, `samesite=strict` cookie and never exposed to client-side code.
- Every `/auth/refresh` call rotates both tokens.

## Database Migrations

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

## Code Quality

```bash
uv run ruff check . --fix
uv run ruff format .
```

Pre-commit hooks are configured; enable them with:

```bash
uv run pre-commit install
```

## Production Checklist

- [ ] `IS_DEBUG=false` — OpenAPI schema is disabled
- [ ] RSA keys provisioned via secret manager, not committed
- [ ] `ALLOW_ORIGINS` restricted to trusted domains
- [ ] TLS terminated at the reverse proxy (refresh cookie is `secure`)
- [ ] Database migrations applied before rollout (`alembic upgrade head`)
- [ ] `/health` wired to your orchestrator's liveness/readiness probes
