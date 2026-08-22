# Deployment and configuration

RyoURL's checked-in Compose file is a development environment. It builds a Python container, starts PostgreSQL and Redis, and exposes the backend on host port `8003`.

## Environment files

Copy the backend template before starting the application:

```bash
cp backend/.env.example backend/.env
```

At minimum, set a unique `SECRET_KEY` and the correct `DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `CORS_ALLOWED_ORIGIN_REGEXES` values. The template uses Compose service names for the database and Redis hosts.

The API test settings are separate. Copy `tests/.env.example` to `tests/.env` and provide a reachable `BASE_URL` plus the normal-user and administrator credentials used by the black-box tests.

## Compose workflow

```bash
docker compose up --build -d
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py migrate'
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py createsuperuser'
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py runserver 0.0.0.0:8000'
```

The server process runs in an interactive `exec` session because the Compose service is intentionally kept available for development commands.

## Production considerations

Before deploying publicly, replace the development server with a production WSGI/ASGI process, set `DEBUG=False`, use secret management, restrict allowed hosts and CORS origins, rotate database credentials, configure durable PostgreSQL and Redis services, and put the frontend and API behind TLS. Review Django's deployment checklist for the target environment.
