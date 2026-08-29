# syntax=docker/dockerfile:1

# ---- frontend: SvelteKit static build (adapter-static → build/) ----
FROM oven/bun:1 AS frontend

WORKDIR /fe

COPY packages/frontend/package.json packages/frontend/bun.lock ./
RUN bun install --frozen-lockfile

COPY packages/frontend/ ./
RUN bun run build


# ---- backend: uv venv with prod deps only ----
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS backend

WORKDIR /app

COPY packages/backend/pyproject.toml packages/backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


# ---- runtime: one process serves the static frontend + API on 8000 ----
FROM python:3.14-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    VDL_FRONTEND_BUILD_DIR=/app/static \
    VDL_SERVE_FRONTEND=true

WORKDIR /app

COPY --from=backend /app/.venv /app/.venv
COPY packages/backend/app ./app
COPY packages/backend/alembic.ini ./
COPY packages/backend/migrations ./migrations
COPY --from=frontend /fe/build ./static

RUN useradd --uid 1000 --create-home app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"]

USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
