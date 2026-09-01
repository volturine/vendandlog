# Vendandlog task runner

default: dev

pytest := 'env -u VIRTUAL_ENV uv run python -m pytest -q'

install:
    cd packages/backend && uv sync
    cd packages/frontend && bun install

# Dev: local Postgres container (:5499) + FastAPI (:8000, runs Alembic migrations + seed) + Vite (:3000, /api proxied).
dev:
    #!/usr/bin/env bash
    set -euo pipefail
    docker compose -f docker/compose.dev.yaml up -d --wait db
    export VDL_DB_URL='postgresql+psycopg://vendandlog:vdl_dev@127.0.0.1:5499/vendandlog'
    (cd packages/backend && env -u VIRTUAL_ENV uv run main.py) &
    backend_pid=$!
    (cd packages/frontend && bun run dev) &
    frontend_pid=$!
    trap 'kill -TERM $backend_pid $frontend_pid 2>/dev/null || true' EXIT INT TERM
    wait

# Stop the local dev database.
dev-db-stop:
    docker compose -f docker/compose.dev.yaml down

# Prod: build the frontend, then FastAPI serves the static build + API from one port.
prod:
    #!/usr/bin/env bash
    set -euo pipefail
    cd packages/frontend && bun run build
    cd ../backend && env -u VIRTUAL_ENV uv run main.py

check:
    cd packages/backend && env -u VIRTUAL_ENV uv run ruff check app tests
    cd packages/frontend && bun run check

format:
    cd packages/backend && env -u VIRTUAL_ENV uv run ruff format app tests && env -u VIRTUAL_ENV uv run ruff check app tests --fix
    cd packages/frontend && bun run format

# Activate the pre-commit hook (formats staged files: ruff + prettier).
hooks:
    git config core.hooksPath .githooks

test:
    cd packages/backend && env -u VIRTUAL_ENV uv run python -m pytest -q

# Build the deployment image. Dev: `just image TAG=ghcr.io/volturine/vendandlog:dev-1`
image TAG='ghcr.io/volturine/vendandlog:dev-1':
    docker build --platform linux/amd64 -f docker/Dockerfile -t {{ TAG }} .
