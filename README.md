# RyoURL

[![CI](https://github.com/KageRyo/RyoURL/actions/workflows/ci.yml/badge.svg)](https://github.com/KageRyo/RyoURL/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/python-3.10-3776AB.svg)](https://www.python.org/)
[![Django 4.2](https://img.shields.io/badge/Django-4.2-092E20.svg)](https://www.djangoproject.com/)

RyoURL is a full-stack URL shortening service built with Django, Django Ninja, PostgreSQL, Redis, and a small static web frontend. It supports anonymous shortening, custom aliases for authenticated users, JWT authentication, expiry management, administration, and API-level testing.

The project is currently maintained as a portfolio and historical full-stack project. The root of this repository is the canonical source for the backend, frontend, schemas, tests, and documentation.

## Features

- Generate six-character random short URLs.
- Create custom aliases for authenticated users.
- Redirect short URLs to their original destinations.
- Track visits using Redis-backed counters.
- Expire and remove URLs automatically when they are accessed after expiry.
- Authenticate users with JWT access and refresh tokens.
- Provide user and administrator API operations.
- Validate API payloads and responses with Pydantic schemas.
- Run black-box API tests and Locust stress tests.

## Repository layout

```text
.
├── backend/
│   ├── manage.py
│   ├── RyoURL/                 # Django project settings and URL configuration
│   ├── shortURL/               # Domain models, API routers, and redirect logic
│   └── schemas/                # Shared Pydantic request/response schemas
├── frontend/                   # Static browser client
├── tests/
│   ├── unit_tests/             # Black-box API tests
│   ├── stress_tests/           # Locust users and scenarios
│   └── actions/                # Reusable API client actions
├── docs/
├── docker-compose.yml
├── requirements.txt
└── pytest.ini
```

## Quick start with Docker Compose

The development compose file starts PostgreSQL, Redis, and a Python development container.

```bash
docker compose up --build -d
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py migrate'
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py runserver 0.0.0.0:8000'
```

The API is then available at `http://127.0.0.1:8003`. Open the frontend in a second terminal:

```bash
python3 -m http.server 5174 --directory frontend --bind 0.0.0.0
```

Open `http://127.0.0.1:5174`. The frontend defaults to `http://127.0.0.1:8003/api`; its API field can be changed when running the services on different ports.

Copy `backend/.env.example` to `backend/.env` before changing application secrets or host settings. Never commit the resulting `.env` file.

## Local Python setup

For a local Python process, install the backend dependencies and provide PostgreSQL and Redis yourself:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example backend/.env
python backend/manage.py migrate
python backend/manage.py runserver 0.0.0.0:8003
```

When services are not running in Compose, set `DB_HOST`, `DB_PORT`, and `REDIS_URL` in `backend/.env` for your local services.

## API and development documentation

- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Database and persistence](docs/database.md)
- [Deployment and configuration](docs/deployment.md)
- [Testing](docs/testing.md)
- [Repository migration and cleanup](docs/repository-migration.md)

The Django Ninja OpenAPI document is served at `/api/openapi.json` while the backend is running.

## Testing

Install the test dependencies, copy `tests/.env.example` to `tests/.env`, start the API, and run:

```bash
pip install -r tests/requirements.txt
pytest
```

The test suite is an API-level suite and expects credentials for a normal user and an administrator. See [Testing](docs/testing.md) for the required environment variables and Locust commands.

## Repository consolidation

The histories of the former `RyoURL-frontend`, `RyoURL-schema`, and `RyoURL-test` repositories were imported into this repository with their commit graphs intact. Their current code lives under `frontend/`, `backend/schemas/`, and `tests/` respectively. The old repositories should be archived after the canonical repository is published; they should not be deleted until their redirect notices and external links have been checked.

## Contributing

Use a standard GitHub Flow branch name such as `feature/<short-description>`, `fix/<short-description>`, or `refactor/<short-description>`. Commit messages follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/), for example:

```text
feat(api): add URL expiry filtering
fix(frontend): handle an expired access token
docs: clarify local setup
```

## License

RyoURL is released under the [MIT License](LICENSE).
