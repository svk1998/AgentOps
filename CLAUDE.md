# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AgentOps — a platform for managing AI agents, optimizing prompts, and routing across cloud and self-hosted LLMs. Split into a FastAPI backend and a Vue 3 SPA frontend, backed by Postgres (with `pgvector`) and Redis.

## Common commands

### Infrastructure (Postgres + Redis)
```bash
docker compose up -d            # start postgres (5432) and redis (6379)
docker compose down             # stop
```

### Backend (FastAPI, from `backend/`)
```bash
pip install -r requirements.txt
alembic upgrade head                        # apply DB migrations
uvicorn main:app --reload --port 8000       # dev server (OpenAPI at /docs)
arq app.workers.tasks.WorkerSettings        # start the ARQ background worker
pytest                                      # run tests (uses tests/conftest.py)
pytest tests/test_auth.py::test_name -q     # run a single test
ruff check . && ruff format .               # lint + format
alembic revision --autogenerate -m "msg"    # create a new migration
python scripts/create_user.py               # create a seed user
```

Tests expect a live Postgres at `postgresql+asyncpg://user:password@localhost:5432/agentops_test` (see `tests/conftest.py`) — the fixture creates/drops all tables each test via `Base.metadata`.

### Frontend (Vue 3 + Vite, from `frontend/`)
```bash
npm install
npm run dev            # vite dev server on :3000, /api proxied to :8000
npm run build          # production bundle
npm run test           # vitest (jsdom)
npm run lint           # eslint --fix (.vue, .js, .jsx)
npm run format         # prettier
```

## Architecture — the big picture

The system has two long-running processes (API + ARQ worker) sharing Postgres and Redis. The frontend is a strictly layered SPA that never talks to Axios from components.

### Backend (`backend/`)

- **Entry:** `main.py` mounts `app.api.v1.router` at `/api`, wires CORS from `settings.ALLOWED_ORIGINS`, and closes the Redis pool on shutdown via lifespan.
- **Config:** `app/core/config.py` — pydantic-settings loaded from `.env`. Holds `DATABASE_URL` (async), `REDIS_URL`, JWT settings, and per-provider LLM keys (Anthropic, OpenAI, Groq, Ollama, vLLM). `DEFAULT_MODEL` is `claude-sonnet-4-6`.
- **DB:** `app/core/database.py` exposes `Base`, `AsyncSessionLocal`, and a `get_db` FastAPI dependency. Models live in `app/models/` (`user`, `agent`, `tool`, `pipeline`, `run`, `prompt_optimization`). Migrations are Alembic (`migrations/`). `pgvector` is used via the `pgvector` package.
- **API v1:** `app/api/v1/{auth,agents,tools,models,pipelines,runs,prompt_optimizer,stats}.py`. Auth deps are in `app/api/deps.py`; JWT/password hashing in `app/core/security.py`.
- **Services layer:** `app/services/llm.py` wraps LiteLLM (one call site for all providers); `app/services/execution.py` runs an agent given a `Run` row — resolves model/system prompt/parameters off the `Agent`, calls `llm.stream`, and invokes an `emit(level, message, data)` callback for log streaming. `app/services/prompt_optimizer.py` implements the Executor → Judge → Refiner loop.
- **Background work:** `app/workers/tasks.py` defines two ARQ tasks:
  - `execute_run` — loads a `Run`, marks it `RUNNING`, calls `run_agent`, persists `RunLog` rows in a batch, and publishes log lines to Redis channel `run:{run_id}:logs`. Terminal sentinel is a log with message `__done__`.
  - `execute_optimization` — iterates the prompt optimizer, persists each `PromptOptimizationIteration`, publishes events (`iteration`, `done`, `stopped`, `error`) to `optimizer:{run_id}`, and honors a stop flag at Redis key `optimizer:stop:{run_id}`.
  - `WorkerSettings` at the bottom of the file is what `arq` loads.
  Enqueue helpers (`enqueue_run`, `enqueue_optimization`) push jobs from API handlers.
- **Logs/events flow to the frontend** via Redis pub/sub — API endpoints subscribe and stream to the browser (check `runs.py` / `prompt_optimizer.py` for the exact transport, e.g. SSE/WebSocket).

### Frontend (`frontend/src/`)

Strictly layered — data flow is **Component → Composable → Store → Service → Axios → Backend**. Components must never import Axios directly. See `docs/architecture.md` (in repo root) for full diagrams.

- **`services/api.js` + `services/interceptors.js`** — the single Axios instance. Request interceptor attaches `Authorization: Bearer <token>`; response interceptor logs out on 401, warns on 403, logs 5xx.
- **`stores/`** — global Pinia stores (`auth`, `user`, `agent`, `promptOptimizer`). `auth` persists the token to localStorage via `pinia-plugin-persistedstate` and rehydrates `user` on boot by calling `GET /auth/me`.
- **`services/*Service.js`** — one file per resource; these are the only things stores call.
- **`modules/<feature>/`** — feature-scoped `views/`, `components/`, `composables/`, and optionally a local store. Global cross-feature concerns live in top-level `components/`, `composables/`, `stores/`.
- **Routing:** `router/index.js` has a single `beforeEach` guard that enforces `guestOnly`, `requiresAuth`, and `requiresRole` route meta. `/login` is the guest route; everything else sits under `DefaultLayout`. `/users` requires `requiresRole: admin`. On auth failure, guard redirects to `/login?redirect=<intended>`.
- **Vite config:** `@` aliases to `src/`. Dev server proxies `/api` → `http://localhost:8000`. Manual chunks split `vendor-vue` and `vendor-http`. Vitest is configured inline here (jsdom environment, globals on).
- **Env:** only `VITE_`-prefixed vars reach the browser. `VITE_API_BASE_URL` points at the backend.

## Conventions worth knowing

- **Python target is 3.10** — `UP017` (use `datetime.UTC`) is disabled in ruff because that's 3.11+. Ruff line length is 100. `known-first-party = ["app"]`. Tests skip `S101`/`ANN`, migrations skip `E501`/`F401`.
- **SQLAlchemy models** use `id` as a PK name — ruff's `A003` (shadowing builtin `id`) is disabled for this reason.
- **bcrypt is pinned to 4.0.1** — passlib is incompatible with bcrypt ≥ 4.1. Don't upgrade without also migrating off passlib.
- **FastAPI `Depends()` in default args** is expected — `B008` is disabled globally.
- **Alembic's `sqlalchemy.url` in `alembic.ini`** is a sync URL (`postgresql://`), while the app itself uses `postgresql+asyncpg://` via `settings.DATABASE_URL`. Keep both in sync when changing DB coordinates.
