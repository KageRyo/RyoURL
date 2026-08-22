# API reference

The default API base URL is `http://127.0.0.1:8003/api`. Requests with a JSON body should use `Content-Type: application/json`. Protected endpoints require `Authorization: Bearer <access-token>`.

## Authentication

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | None | Create a user and return access/refresh tokens. |
| `POST` | `/auth/login` | None | Authenticate a user and return access/refresh tokens. |

Registration and login accept `username` and `password`.

## Public and authenticated URL operations

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| `POST` | `/short-url/short` | Optional | Create a random six-character short URL. |
| `GET` | `/short-url/origin/{short_string}` | None | Look up the original URL and metadata. |
| `POST` | `/short-url-with-auth/custom` | User | Create a custom short alias. |
| `GET` | `/short-url-with-auth/all-my` | User | List URLs owned by the current user. |
| `DELETE` | `/short-url-with-auth/url/{short_string}` | User/admin | Delete an owned URL; administrators may delete any URL. |

Random and custom URL creation accepts `origin_url` and an optional `expire_date`. Custom creation also accepts `short_string`.

## User operations

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/user/info?username={username}` | User/admin | Read the current user's information; administrators may inspect any user. |
| `POST` | `/user/refresh-token` | User | Exchange a refresh token for a new access token. |

## Administrator operations

| Method | Endpoint | Authentication | Purpose |
| --- | --- | --- | --- |
| `GET` | `/admin/all-urls` | Administrator | List all URL records. |
| `DELETE` | `/admin/expire-urls` | Administrator | Delete records whose expiry is in the past. |
| `GET` | `/admin/users` | Administrator | List users and their roles. |
| `PUT` | `/admin/user/{username}?user_type={0\|1\|2}` | Administrator | Change a user's role. |
| `DELETE` | `/admin/user/{username}` | Administrator | Delete a user. |

## Redirect endpoint and OpenAPI

The short URL redirect is outside the API namespace:

```text
GET /{short_string}/
```

The generated Django Ninja OpenAPI document is available at:

```text
GET /api/openapi.json
```
