# Architecture

RyoURL is organized as one application with four runtime-facing parts: a Django API, a browser frontend, shared Pydantic schemas, and API/stress tests.

```text
Browser
  │
  ▼
Static frontend (frontend/)
  │  HTTP + JSON, JWT bearer token when authenticated
  ▼
Django Ninja API (backend/)
  ├── Authentication and authorization
  ├── URL creation, lookup, deletion, and administration
  ├── Redirect view for /<short_string>/
  └── Pydantic schemas (backend/schemas/)
       │                 │
       ▼                 ▼
  PostgreSQL          Redis
  users and URLs      visit-count cache
```

## Backend

`backend/manage.py` is the Django entry point. The Django project package is `backend/RyoURL/`, while the application package is `backend/shortURL/`.

The API is assembled in `backend/shortURL/api.py` and exposes routers for authentication, basic URL operations, authenticated URL operations, user operations, and administrator operations. `backend/RyoURL/urls.py` also exposes the redirect view and the Django administration site.

## Authentication

Registration and login return a JWT access token and refresh token. Protected endpoints use the access token in an `Authorization: Bearer <token>` header. Administrator endpoints require a user with `user_type == 2`.

## Persistence and caching

PostgreSQL stores users and URL records. Redis caches visit counters so redirects do not write to PostgreSQL for every request. The application periodically flushes cached counts back to the database and falls back to a direct database update if Redis is unavailable.

## Frontend

The frontend is intentionally dependency-light: `frontend/index.html`, `frontend/app.js`, and `frontend/styles.css` form a static client. It can be served by Python's built-in HTTP server or any static file server. The API base URL is configurable in the page header.

## Tests

The tests in `tests/unit_tests/` exercise the running HTTP API rather than importing backend internals. `tests/stress_tests/` contains Locust users for anonymous, authenticated, and administrator traffic. Both suites use the shared schemas from `backend/schemas/`.
