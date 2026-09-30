# Days 14–15 — Authentication

## Day 14
- Registration and login endpoints
- Argon2 password hashing via `pwdlib`
- JWT access tokens with expiry
- Authentication schemas and security configuration

## Day 15
- Bearer authentication dependency
- Protected `/api/v1/me` route
- JWT signature and expiry validation
- Active-user validation
- Standard 401/403 responses

## Endpoints
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/me` with `Authorization: Bearer <token>`

Passwords are stored only as password hashes. JWT payload contains the user ID subject and expiry.

Runtime validation requires PostgreSQL and installed dependencies; GitHub repository operations do not execute the runtime environment.
