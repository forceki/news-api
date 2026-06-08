# FastAPI News API

A news management API built with FastAPI, featuring JWT authentication, topic categorization, Redis caching, and auto-generated slugs.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (package manager)
- [Moonrepo](https://moonrepo.dev/docs/getting-started/installation) (optional, task runner)
- PostgreSQL
- Redis
- Docker and Docker Compose (optional, for containerized development)

## Installation

1. Set up environment variables:

    ```bash
    cp .env.example .env
    # Edit .env with your configuration
    ```

2. Install dependencies:

    ```bash
    uv sync
    ```

3. Run database migrations:

    ```bash
    uv run alembic upgrade head
    ```

4. (Optional) Seed the database:

    ```bash
    uv run python -m app.database.seeder.main
    ```

## Environment Variables

| Variable                     | Description                              | Default                      |
|------------------------------|------------------------------------------|------------------------------|
| `ML_PREFIX_API`              | API root path prefix                     | `/api`                       |
| `APP_NAME`                   | Application name                         | `news-api`                   |
| `APP_ENVIRONMENT`            | Environment (`development`/`production`) | `development`                |
| `DATABASE_URL`               | PostgreSQL connection string             | -                            |
| `REDIS_URL`                  | Redis connection string                  | `redis://localhost:6379/0`   |
| `OPENAI_API_KEY`             | OpenAI API key                           | -                            |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry exporter endpoint        | `localhost:4317`             |
| `JWT_SECRET_KEY`             | Secret key for JWT token signing         | -                            |
| `JWT_ALGORITHM`              | JWT signing algorithm                    | `HS256`                      |
| `JWT_EXPIRATION_MINUTES`     | JWT token expiration in minutes          | `30`                         |

## Running the Application

### Development Mode

```bash
uv run fastapi dev app/main.py --port 8080
```

### Production Mode

```bash
uv run fastapi run app/main.py --port 8080
```

### Using Moonrepo

```bash
moon fastapi-ai:dev       # Development server
moon fastapi-ai:start     # Production server
moon fastapi-ai:sync      # Install dependencies
moon fastapi-ai:migrate   # Run migrations
moon fastapi-ai:seed      # Seed database
```

Once running, the Swagger UI is available at `http://localhost:8080/api/docs`.

## API Endpoints

### Authentication (`/auth`)

| Method | Path              | Auth | Description                      |
|--------|-------------------|------|----------------------------------|
| POST   | `/auth/register`  | No   | Register a new user              |
| POST   | `/auth/login`     | No   | Login and receive JWT token      |
| GET    | `/auth/me`        | JWT  | Get current authenticated user   |

### Topics (`/topics`) - All endpoints require JWT

| Method | Path               | Description            |
|--------|--------------------|------------------------|
| GET    | `/topics`          | List all topics        |
| GET    | `/topics/{id}`     | Get topic by ID        |
| POST   | `/topics`          | Create a topic         |
| PUT    | `/topics/{id}`     | Update a topic         |
| DELETE | `/topics/{id}`     | Delete a topic         |

### News (`/news`) - All endpoints require JWT

| Method | Path             | Query Params                                       | Description                        |
|--------|------------------|----------------------------------------------------|------------------------------------|
| GET    | `/news`          | `topic_id`, `news_status`, `search`, `page`, `limit` | List news with filters & pagination |
| GET    | `/news/{id}`     |                                                    | Get news by ID                     |
| POST   | `/news`          |                                                    | Create news (accepts `topic_ids`)  |
| PUT    | `/news/{id}`     |                                                    | Update news                        |
| DELETE | `/news/{id}`     |                                                    | Delete news                        |

### Public (`/public`) - No authentication required

| Method | Path                  | Query Params                                       | Cache  | Description              |
|--------|-----------------------|----------------------------------------------------|--------|--------------------------|
| GET    | `/public/news`        | `status`, `topic_id`, `search`, `page`, `limit`   | Redis  | List news with filters   |
| GET    | `/public/news/{slug}` |                                                    | Redis  | Get news by slug         |

### Other

| Method | Path              | Description                      |
|--------|-------------------|----------------------------------|
| GET    | `/`               | Welcome message                  |
| GET    | `/health-check`   | Database connection health check |
| GET    | `/openai/greetings` | OpenAI greeting example        |

## Slugs

Slugs are **auto-generated** from the `name` (topics) or `title` (news):

```
"Machine Learning"  →  "machine-learning"
"Breaking News!"    →  "breaking-news"
```

- On **create**: slug is generated from name/title
- On **update**: changing name/title auto-regenerates the slug
- Slugs are unique and used for public-facing URLs

## Project Structure

```
app/
├── core/                   # Core utilities & infrastructure
│   ├── cache.py            # Redis cache (fallback: in-memory)
│   ├── database.py         # SQLAlchemy async engine & session
│   ├── env.py              # Environment configuration (Pydantic)
│   ├── exception.py        # Custom AppError exception
│   ├── instrumentation.py  # OpenTelemetry & Prometheus
│   ├── logging.py          # Logging with request ID middleware
│   ├── response.py         # Generic response models
│   ├── security.py         # JWT & bcrypt password utilities
│   └── slug.py             # Auto slug generation
├── model/                  # SQLAlchemy ORM models
│   ├── user.py
│   ├── topic.py
│   └── news.py             # News model + news_topics junction table
├── schemas/                # Pydantic request/response schemas
│   ├── auth.py
│   ├── topic.py
│   └── news.py
├── repository/             # Data access layer
│   ├── user.py
│   ├── topic.py
│   ├── news.py
│   └── openai/
│       ├── greeting.py
│       └── dependency.py
├── services/               # Business logic layer
│   ├── auth.py
│   ├── topic.py
│   ├── news.py
│   ├── greeting.py
│   └── dependency.py
├── router/                 # API route handlers
│   ├── auth.py
│   ├── topic.py
│   ├── news.py
│   ├── public.py
│   ├── root.py
│   └── openai.py
├── database/
│   ├── migration/          # Alembic migrations
│   └── seeder/             # Database seeders
└── main.py                 # FastAPI app entry point
```

## Database Schema

### Tables

- **users** - User accounts with bcrypt password hashing
- **topics** - News categories with unique name/slug
- **news** - News articles with status, published_at, and author tracking
- **news_topics** - Many-to-many junction between news and topics

### Key Indexes

- `ix_news_slug` (unique) - Fast lookup by slug
- `idx_news_status_published` - Composite index on `(status, published_at DESC)` for filtering
- `ix_news_author_id` - Filter by author
- `ix_topics_name` / `ix_topics_slug` (unique) - Fast topic lookups
- `ix_news_topics_news_id` / `ix_news_topics_topic_id` - Fast junction table joins

## Caching

The API uses **Redis** for caching public endpoints with automatic fallback to in-memory cache if Redis is unavailable.

- **Cache key strategy**: MD5 hash of request path + sorted query params
- **TTL**: 3600 seconds (1 hour)
- **Invalidation**: All `public:news:*` keys are flushed on create/update/delete
- **Fallback**: If Redis connection fails, automatically uses in-memory cache

```
GET /public/news?page=1&status=1  →  key: public:news:list:<md5hash>
GET /public/news/my-article       →  key: public:news:slug:<md5hash>
```

## Authentication

The API uses JWT Bearer token authentication. To access protected endpoints:

1. Register a user via `POST /auth/register`
2. Login via `POST /auth/login` to receive an `access_token`
3. Include the token in the `Authorization` header:

    ```
    Authorization: Bearer <access_token>
    ```

To protect any new endpoint, add `DepCurrentUser` as a dependency:

```python
from app.core.security import DepCurrentUser

@router.get("/protected")
async def protected_route(current_user: DepCurrentUser):
    return {"user_id": current_user["sub"]}
```

## Error Handling

A global exception handler catches every `AppError` and returns a structured JSON response:

```python
from app.core.exception import AppError

raise AppError(
    message="Invalid user ID",
    status_code=400,
    code="INVALID_ID",
    data={"user_id": supplied_id}
)
```

Response:

```json
{
  "success": false,
  "message": "Invalid user ID",
  "error_code": "INVALID_ID",
  "data": { "user_id": 123 }
}
```

## Testing

```bash
# Install test dependencies
uv sync --extra test

# Run tests
uv run pytest -v
```

- 48 tests covering auth, topics, news, and public endpoints
- Uses in-memory SQLite + in-memory cache (no Redis/PostgreSQL needed)
- CI runs automatically via GitHub Actions on push/PR to main

## Migration Commands

| Command                                              | Description                                    |
|------------------------------------------------------|------------------------------------------------|
| `uv run alembic upgrade head`                        | Apply all pending migrations                   |
| `uv run alembic revision -m "description"`           | Create a new empty migration                   |
| `uv run alembic revision --autogenerate -m "desc"`   | Auto-generate migration from model changes     |
| `uv run alembic downgrade -1`                        | Rollback the last migration                    |
| `uv run alembic downgrade base`                      | Reset all migrations                           |
