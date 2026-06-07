# Prompt History

A log of prompts used to build this project with Claude Code.

---

## 1. Create Auth Endpoints (Register & Login) + Middleware

**Prompt:**
> so first I want to make endpoint for register users and login user, please create middleware for autho too

**Result:**
- Created `app/schemas/auth.py` — `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserResponse`
- Created `app/repository/user.py` — `UserRepository` (get_by_username, get_by_email, create)
- Created `app/services/auth.py` — `AuthService` (register, login with password hashing & JWT)
- Created `app/core/security.py` — JWT creation/decode, bcrypt password hashing, `DepCurrentUser` middleware
- Created `app/router/auth.py` — `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Added `pyjwt` and `passlib[bcrypt]` to `pyproject.toml`
- Added `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES` to `app/core/env.py`
- Wired `auth_router` into `app/main.py`

---

## 2. Fix bcrypt Password Length Error

**Prompt:**
> ValueError: password cannot be longer than 72 bytes, truncate manually if necessary

**Result:**
- Added `_prepare_password()` — SHA-256 pre-hash before bcrypt to support any password length

---

## 3. Fix passlib + bcrypt Incompatibility

**Prompt:**
> AttributeError: module 'bcrypt' has no attribute '__about__'

**Result:**
- Replaced `passlib` with direct `bcrypt` usage in `app/core/security.py`
- Changed dependency from `passlib[bcrypt]` to `bcrypt>=4.0.0` in `pyproject.toml`

---

## 4. Create Topics Feature (Migration + CRUD)

**Prompt:**
> create migration table topics & create new CRUD
>
> ```sql
> CREATE TABLE topics (
>     id INT AUTO_INCREMENT PRIMARY KEY,
>     name VARCHAR(100) NOT NULL UNIQUE,
>     slug VARCHAR(100) NOT NULL UNIQUE,
>     created_by INT NULL,
>     updated_by INT NULL,
>     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
>     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
> );
> CREATE INDEX for fastest query filter
> ```

**Result:**
- Created `app/model/topic.py` — `Topic` model with FK to `users`
- Created `app/schemas/topic.py` — `TopicCreateRequest`, `TopicUpdateRequest`, `TopicResponse`
- Created `app/repository/topic.py` — `TopicRepository` (get_all, get_by_id, get_by_slug, get_by_name, create, update, delete)
- Created `app/services/topic.py` — `TopicService` with uniqueness validation
- Created `app/router/topic.py` — CRUD endpoints under `/topics`
- Created migration `a1b2c3d4e5f6_create_topics_table.py`
- Indexes: `ix_topics_name` (unique), `ix_topics_slug` (unique), `ix_topics_created_by`, `ix_topics_updated_by`

---

## 5. Create News Feature (Migration + CRUD)

**Prompt:**
> I want to create feature news, I have attached the raw table for migration
>
> ```sql
> CREATE TABLE news (...);
> CREATE INDEX idx_news_status_published ON news(status, published_at DESC);
> CREATE TABLE news_topics (...);
> ```

**Result:**
- Created `app/model/news.py` — `News` model + `news_topics` junction table with relationship to `Topic`
- Created `app/schemas/news.py` — `NewsCreateRequest`, `NewsUpdateRequest`, `NewsResponse` (with nested topics)
- Created `app/repository/news.py` — `NewsRepository` with `selectinload` for topics
- Created `app/services/news.py` — `NewsService` with slug uniqueness & topic ID validation
- Created `app/router/news.py` — CRUD endpoints under `/news`
- Created migration `b2c3d4e5f6a7_create_news_tables.py`
- Indexes: `ix_news_slug` (unique), `idx_news_status_published` (composite), `ix_news_author_id`, junction table indexes

---

## 6. Add JWT Middleware to GET Endpoints

**Prompt:**
> add this using middleware (selected `@router.get("/{news_id}")`, `@router.get("/{topic_id}")`)

**Result:**
- Added `DepCurrentUser` to `GET /news` and `GET /news/{news_id}` — all news endpoints now require JWT
- Added `DepCurrentUser` to `GET /topics` and `GET /topics/{topic_id}` — all topic endpoints now require JWT

---

## 7. Create Public News Endpoint with Cache

**Prompt:**
> create endpoint for public user using slug for get news add cache

**Result:**
- Created `app/core/cache.py` — `InMemoryCache` with TTL (60s) and prefix invalidation
- Created `app/router/public.py` — `GET /public/news/{slug}` (no auth, cached)
- Updated `app/repository/news.py` — `get_by_slug` now loads topics via `selectinload`
- Added `get_by_slug()` to `app/services/news.py`
- Wired `public_router` into `app/main.py`

---

## 8. Update README

**Prompt:**
> please update README.md using current logic

**Result:**
- Rewrote `README.md` with full project documentation: endpoints, project structure, database schema, auth flow, env variables, migration commands

---

## 9. Unit Test Suite + CI Pipeline

**Prompt:**
> Writing a unit test suite. Setting up CI pipeline to run unit tests. please setup this

**Result:**
- Added test dependencies to `pyproject.toml`: `pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`
- Added `[tool.pytest.ini_options]` config with `asyncio_mode = "auto"`
- Created `tests/conftest.py` — shared fixtures:
  - In-memory SQLite database (replaces PostgreSQL `now()` with `CURRENT_TIMESTAMP`)
  - Async test client via `httpx.AsyncClient`
  - `auth_token` fixture (registers user + logs in)
  - Auto-reset database & cache between tests
- Created `tests/test_auth.py` — 9 tests: register (success, duplicate username/email, missing fields), login (success, wrong password, nonexistent user), me (authenticated, unauthenticated)
- Created `tests/test_topics.py` — 10 tests: create (success, unauth, duplicate name/slug), get all/by-id/not-found/unauth, update (success, not found), delete (success, not found)
- Created `tests/test_news.py` — 14 tests: create (success, with topics, unauth, duplicate slug, invalid topic IDs), get all/by-id/not-found/unauth, update (success, change topics, not found), delete (success, not found, unauth)
- Created `tests/test_public.py` — 4 tests: get by slug (success, not found, cached, no auth required)
- Created `.github/workflows/test.yml` — GitHub Actions CI: Python 3.12, uv, runs on push/PR to main
- **Total: 40 tests, all passing**
