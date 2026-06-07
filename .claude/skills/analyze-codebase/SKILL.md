---
name: analyze-codebase
description: Perform a comprehensive analysis of the current codebase. Use when the user asks to analyze, audit, review, or understand the project structure, architecture, dependencies, or code quality.
user-invocable: true
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Agent
argument-hint: [focus-area]
arguments: [focus]
effort: high
---

## Codebase Analysis Skill

You are performing a comprehensive codebase analysis. Analyze the project thoroughly and produce a structured report.

If a focus area is provided: **$focus** — narrow the analysis to that area. Otherwise, perform a full analysis.

## Step 1: Gather Project Context

Collect the following information:

- **Project root**: Identify the main language, framework, and project type
- **Package manifest**: Read `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, or equivalent
- **Entry point**: Identify how the app starts
- **Environment config**: Check for `.env.example`, settings files, config loaders
- **CI/CD**: Check for `.github/workflows/`, `Dockerfile`, `docker-compose.yml`, `Makefile`, `moon.yml`
- **Git state**: !`git log --oneline -10 2>/dev/null || echo "Not a git repo"`

## Step 2: Architecture Analysis

Map out the project structure:

1. **Directory layout** — List all top-level and important nested directories with their purpose
2. **Layered architecture** — Identify layers (routers/controllers, services, repositories, models, schemas, middleware, etc.)
3. **Request flow** — Trace a typical request from entry to response
4. **Dependency injection** — How are dependencies wired together?
5. **Database setup** — ORM, migrations, seeders, connection management
6. **External integrations** — Third-party APIs, message queues, caches

## Step 3: Code Quality Assessment

Evaluate the following:

- **Patterns used**: Design patterns (repository, singleton, factory, etc.)
- **Error handling**: How are errors caught, propagated, and returned?
- **Logging & observability**: Structured logging, tracing, metrics
- **Type safety**: Type hints, validation (Pydantic, Zod, etc.)
- **Security posture**: Authentication, authorization, input validation, CORS, secrets management
- **Test coverage**: Presence of tests, test structure, test utilities

## Step 4: Dependency Audit

- List all direct dependencies with their purpose
- Flag any outdated, deprecated, or potentially problematic dependencies
- Note dev vs production dependencies

## Step 5: Gaps & Recommendations

Identify:

- **Missing features**: Auth, tests, error handling, validation, documentation
- **Security concerns**: Hardcoded secrets, open CORS, missing rate limiting
- **Code smells**: Dead code, unused imports, inconsistent patterns
- **Scalability concerns**: Blocking calls, missing connection pooling, N+1 queries

## Output Format

Present the analysis as a structured report with these sections:

```
## Project Overview
(name, framework, language, purpose)

## Architecture
(directory structure, layers, request flow diagram)

## Key Components
(table of components with file path and description)

## Dependencies
(categorized list with purpose)

## Design Patterns
(patterns identified with examples)

## Security Assessment
(current posture + recommendations)

## Code Quality
(strengths + areas for improvement)

## Gaps & Recommendations
(prioritized list: critical > important > nice-to-have)
```

Keep the report factual and actionable. Reference specific files using markdown links like [filename.py](path/to/filename.py).
