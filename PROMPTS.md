# Prompt History

A log of all AI prompts used to build this project. This project was built entirely using **Claude Code** (Anthropic's CLI agent) as an AI-assisted development tool.

## How AI Was Used

- **Tool:** [Claude Code](https://claude.ai/claude-code) (CLI agent powered by Claude)
- **Approach:** Prompt-driven development — each feature was described in natural language, and Claude Code generated the full implementation (models, schemas, services, repositories, routers, migrations, tests, CI pipeline).
- **Human role:** Providing requirements, reviewing generated code, reporting runtime errors for fixes, and guiding architecture decisions.
- **AI role:** Code generation, bug fixing, test writing, CI setup, documentation, and system design.

## What AI Generated

| Area | Files | Description |
|------|-------|-------------|
| Auth | `security.py`, `auth.py` (router/service/schema/repo) | JWT + bcrypt authentication system |
| Topics CRUD | `topic.py` (model/router/service/schema/repo) | Full CRUD with uniqueness validation |
| News CRUD | `news.py` (model/router/service/schema/repo) | CRUD with many-to-many topic relations |
| Public API | `public.py`, `cache.py` | Cached public endpoints with MD5 cache keys |
| Migrations | 3 Alembic migration files | Database schema for users, topics, news, news_topics |
| Tests | 4 test files, `conftest.py` | 46 unit tests using pytest + in-memory SQLite |
| CI/CD | `.github/workflows/test.yml` | GitHub Actions pipeline |
| Docs | `README.md`, `SYSTEM_DESIGN.md` | Full project documentation + Mermaid diagrams |

---

## Prompt Log

### 1. Create Auth Endpoints (Register & Login) + Middleware

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

### 2. Fix bcrypt Password Length Error

**Prompt:**
> ValueError: password cannot be longer than 72 bytes, truncate manually if necessary

**Result:**
- Added `_prepare_password()` — SHA-256 pre-hash before bcrypt to support any password length

---

### 3. Fix passlib + bcrypt Incompatibility

**Prompt:**
> AttributeError: module 'bcrypt' has no attribute '__about__'

**Result:**
- Replaced `passlib` with direct `bcrypt` usage in `app/core/security.py`
- Changed dependency from `passlib[bcrypt]` to `bcrypt>=4.0.0` in `pyproject.toml`

---

### 4. Create Topics Feature (Migration + CRUD)

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

### 5. Create News Feature (Migration + CRUD)

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

### 6. Add JWT Middleware to GET Endpoints

**Prompt:**
> add this using middleware (selected `@router.get("/{news_id}")`, `@router.get("/{topic_id}")`)

**Result:**
- Added `DepCurrentUser` to `GET /news` and `GET /news/{news_id}` — all news endpoints now require JWT
- Added `DepCurrentUser` to `GET /topics` and `GET /topics/{topic_id}` — all topic endpoints now require JWT

---

### 7. Create Public News Endpoint with Cache

**Prompt:**
> create endpoint for public user using slug for get news add cache

**Result:**
- Created `app/core/cache.py` — `InMemoryCache` with TTL (60s) and prefix invalidation
- Created `app/router/public.py` — `GET /public/news/{slug}` (no auth, cached)
- Updated `app/repository/news.py` — `get_by_slug` now loads topics via `selectinload`
- Added `get_by_slug()` to `app/services/news.py`
- Wired `public_router` into `app/main.py`

---

### 8. Update README

**Prompt:**
> please update README.md using current logic

**Result:**
- Rewrote `README.md` with full project documentation: endpoints, project structure, database schema, auth flow, env variables, migration commands

---

### 9. Unit Test Suite + CI Pipeline

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

---

### 10. Add Public Get All News + MD5 Cache Keys

**Prompt:**
> please add getall news for public and add cache identified using all params from request convert to md5

**Result:**
- Added `GET /public/news` with query params: `status`, `topic_id`, `search`, `page`, `limit`
- Cache key generated by MD5-hashing sorted request path + query params
- Added `get_all_public()` to repository (with filtering, search, pagination) and service
- Added `metadata` support to `success_response()` (page, limit, total, total_pages)
- Updated `tests/test_public.py` — 6 new tests: get all, pagination, filter by status, search, MD5 cache, no auth
- **Total: 46 tests, all passing**

---

### 11. Cache Invalidation on News Mutations

**Prompt:**
> so please update function create and update news when has changed the attribute please flush the cache

**Result:**
- Added `cache.invalidate_prefix("public:news:")` to `NewsService.create()`, `update()`, and `delete()`
- All public news cache is flushed whenever news is created, updated, or deleted

---

### 12. System Design Diagram

**Prompt:**
> System Design create text to diagram please using excalidraw store to .md file

**Result:**
- Created `SYSTEM_DESIGN.md` with 7 Mermaid diagrams:
  - Architecture overview (full system topology)
  - Authenticated request flow (sequence diagram)
  - Public request with cache (sequence diagram with hit/miss)
  - Database ERD (users, topics, news, news_topics)
  - Layered architecture (router → service → repository → model)
  - Cache strategy (MD5 key generation + invalidation flow)
  - CI/CD pipeline

---

### 13. Auto-Generate Slug from Name/Title

**Prompt:**
> slug news and topics that from name or title create slug auto generate

**Result:**
- Created `app/core/slug.py` — `slugify()` utility (unicode-safe, lowercased, hyphenated)
- Made `slug` optional in `TopicCreateRequest` and `NewsCreateRequest` schemas
- Updated `TopicService` and `NewsService` to auto-generate slug from `name`/`title` on create
- On update: changing `name`/`title` auto-regenerates slug
- Updated all tests to use auto-generated slugs

---

### 14. Remove Slug from Request Payloads

**Prompt:**
> remove slug Request body post payload

**Result:**
- Removed `slug` field entirely from `TopicCreateRequest`, `TopicUpdateRequest`, `NewsCreateRequest`, `NewsUpdateRequest`
- Slug is now always auto-generated — no manual override
- Services always use `slugify()` from name/title
- Updated all tests to remove `slug` from request payloads
- **Total: 48 tests, all passing**

---

### 15. Add Filters to Authenticated News Endpoint

**Prompt:**
> please this add filter topic and status (selected `get_all_news`)

**Result:**
- Added query params to `GET /news`: `topic_id`, `news_status`, `search`, `page`, `limit`
- Reuses `get_all_public()` from service/repository for filtering and pagination
- Returns pagination `metadata` (page, limit, total, total_pages)

---

### 16. Add Redis for Cache

**Prompt:**
> add redis for cache

**Result:**
- Rewrote `app/core/cache.py` with two implementations:
  - `RedisCache` — uses `redis-py` with JSON serialization, `SCAN`-based prefix invalidation
  - `InMemoryCache` — kept as fallback for testing or when Redis is unavailable
- Auto-detection: uses Redis in dev/production, falls back to `InMemoryCache` if connection fails
- Added `redis>=5.0.0` to `pyproject.toml`
- Added `REDIS_URL` to `app/core/env.py` (default: `redis://localhost:6379/0`)
- Updated `.env.example` and `.github/workflows/test.yml`
- Updated `tests/conftest.py` to patch cache with `InMemoryCache` for tests
- **Total: 48 tests, all passing**
