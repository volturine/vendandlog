# Vendandlog task runner

default: dev

pytest := 'env -u VIRTUAL_ENV uv run python -m pytest -q'

install:
    cd packages/backend && uv sync
    cd packages/frontend && bun install

# Dev: FastAPI on :8000 (SQLite + seed on first run), SvelteKit dev server on :3000 with /api proxy.
dev:
    #!/usr/bin/env bash
    set -euo pipefail
    (cd packages/backend && env -u VIRTUAL_ENV uv run main.py) &
    backend_pid=$!
    (cd packages/frontend && bun run dev) &
    frontend_pid=$!
    trap 'kill -TERM $backend_pid $frontend_pid 2>/dev/null || true' EXIT INT TERM
    wait

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

test:
    cd packages/backend && env -u VIRTUAL_ENV uv run python -m pytest -q
