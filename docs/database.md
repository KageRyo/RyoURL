# Database and persistence

## PostgreSQL

The default Compose database is PostgreSQL 13. Django migrations are stored in `backend/shortURL/migrations/` and should be applied with:

```bash
docker compose exec web sh -lc 'cd /workspace/backend && python manage.py migrate'
```

The main application models are:

- `User`: Django's user fields plus `user_type` (`0` anonymous, `1` normal user, `2` administrator).
- `Url`: the original URL, short alias, generated short URL, creation/expiry timestamps, visit count, and optional creator.

The API request and response models are the Pydantic classes in `backend/schemas/schemas.py`. They are part of the backend runtime and are no longer a Git submodule.

## Redis

Redis stores temporary visit counters and daily flush markers. The default URL is `redis://redis:6379/1` in Compose. If Redis is unavailable, redirects fall back to a direct PostgreSQL counter update.

## Configuration

Database and Redis settings are read from `backend/.env`:

```text
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=postgresql
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
```

Use different credentials and managed services for any public deployment. Do not commit real credentials or production data.
