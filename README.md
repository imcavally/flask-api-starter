# Flask API Starter

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A small, production-shaped REST API starter built with **Flask 3** and
**SQLAlchemy 2**. It demonstrates the patterns a real backend needs on day
one — JWT authentication with refresh tokens, role-based access control,
auto-generated OpenAPI docs, database migrations, consistent JSON errors,
pagination and filtering — in a codebase deliberately kept small enough to
read in one sitting.

## Features

- **Flask 3 + SQLAlchemy 2** — application factory, typed `Mapped[]` models
- **flask-smorest** — OpenAPI 3 spec generated from marshmallow schemas, Swagger UI at [`/docs`](http://localhost:5000/docs)
- **JWT auth** (flask-jwt-extended) — register, login, refresh tokens, `GET /me`
- **RBAC** — `admin` / `user` roles baked into token claims, `@role_required` decorator
- **Sample resource** — `projects` CRUD with pagination, status filter, name search, and ownership rules
- **Consistent JSON errors** — one error shape for validation, auth, 404s, and crashes
- **Alembic migrations** via flask-migrate, plus a `flask seed-admin` CLI command
- **SQLite by default, Postgres via `DATABASE_URL`** — no config needed to start
- **Tests** (pytest) and **linting** (ruff) wired into GitHub Actions CI
- **Dockerfile + docker-compose** (API + Postgres) for one-command deployment

## Quickstart

Three commands, no configuration:

```bash
python -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app wsgi db upgrade && .venv/bin/flask --app wsgi seed-admin
.venv/bin/flask --app wsgi run --debug
```

(On Windows, replace `.venv/bin/` with `.venv\Scripts\`.)

Then open **http://localhost:5000/docs** for interactive Swagger UI, or:

```bash
curl -X POST localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "change-me-please"}'
```

With Docker instead:

```bash
docker compose up --build
# API on http://localhost:8000, backed by Postgres
```

## API overview

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/v1/health` | — | Liveness probe |
| `POST` | `/api/v1/auth/register` | — | Create an account |
| `POST` | `/api/v1/auth/login` | — | Get access + refresh tokens |
| `POST` | `/api/v1/auth/refresh` | refresh token | New access token |
| `GET` | `/api/v1/auth/me` | access token | Current user profile |
| `GET` | `/api/v1/projects` | access token | List own projects (admin: all). Supports `page`, `per_page`, `status`, `q` |
| `POST` | `/api/v1/projects` | access token | Create a project |
| `GET` | `/api/v1/projects/{id}` | access token | Get one project (owner or admin) |
| `PATCH` | `/api/v1/projects/{id}` | access token | Partial update (owner or admin) |
| `DELETE` | `/api/v1/projects/{id}` | **admin** | Delete a project |

List responses use a pagination envelope:

```json
{
  "items": [ ... ],
  "meta": { "page": 1, "per_page": 10, "total": 25, "pages": 3 }
}
```

All errors share one shape:

```json
{ "code": 403, "status": "Forbidden", "message": "You do not have permission to perform this action." }
```

## Project structure

```
flask-api-starter/
├── app/
│   ├── __init__.py        # application factory
│   ├── config.py          # env-driven config (dev / testing / production)
│   ├── extensions.py      # db, migrate, jwt, api singletons
│   ├── authz.py           # current_user() + @role_required RBAC decorator
│   ├── errors.py          # consistent JSON error handlers (incl. JWT)
│   ├── cli.py             # `flask seed-admin`
│   ├── api/               # flask-smorest blueprints (auth, projects, health)
│   ├── models/            # SQLAlchemy 2 typed models (User, Project)
│   └── schemas/           # marshmallow request/response schemas
├── migrations/            # Alembic migration scripts
├── tests/                 # pytest suite: auth flow, RBAC, CRUD, pagination
├── Dockerfile
├── docker-compose.yml     # api + postgres
├── Makefile               # install / run / test / lint / migrate / seed
└── .github/workflows/ci.yml
```

## Development

```bash
make install   # venv + dev dependencies
make test      # pytest
make lint      # ruff check
make migrate m="add widgets table"   # autogenerate a migration
make upgrade   # apply migrations
```

Configuration is environment-driven — copy `.env.example` to `.env` and
adjust. Point `DATABASE_URL` at Postgres to switch databases; nothing else
changes.

## How to extend

Adding a new resource takes four small steps, each mirrored by an existing
example:

1. **Model** — add `app/models/widget.py` with a typed SQLAlchemy model
   (copy `project.py`), export it from `app/models/__init__.py`.
2. **Schemas** — add request/response marshmallow schemas in
   `app/schemas/widget.py` (copy `project.py`; reuse `PaginationMetaSchema`).
3. **Blueprint** — add `app/api/widgets.py` with a flask-smorest `Blueprint`
   and `MethodView` classes, then register it in `create_app()`. Use
   `@jwt_required()` for authentication and `@role_required("admin")` where
   only admins should act.
4. **Migrate + test** — `make migrate m="add widgets"`, `make upgrade`, and
   add tests under `tests/` (fixtures for users, admins, and auth headers
   already exist in `conftest.py`).

## License

[MIT](LICENSE) — Trung P.
