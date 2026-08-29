from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db import init_db
from app.routers import conversations, listings, misc, users

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    from app.seed import ensure_seeded

    ensure_seeded()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title='Vendandlog', version='0.1.0', docs_url='/api/docs', openapi_url='/api/openapi.json', lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.include_router(misc.router)
    app.include_router(users.router)
    app.include_router(listings.router)
    app.include_router(conversations.router)

    if settings.serve_frontend and settings.frontend_build_dir.is_dir():
        _mount_frontend(app, settings.frontend_build_dir)

    return app


def _mount_frontend(app: FastAPI, build_dir: Path) -> None:
    """Serve the statically built SvelteKit app. Unknown non-API paths fall back to 200.html (SPA)."""
    assets = build_dir / '_app'
    if assets.is_dir():
        app.mount('/_app', StaticFiles(directory=assets), name='assets')

    @app.get('/{full_path:path}', include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith('api'):
            raise HTTPException(404, 'Not found')
        candidate = (build_dir / full_path).resolve()
        if candidate.is_file() and build_dir in candidate.parents:
            return FileResponse(candidate)
        fallback = build_dir / '200.html'
        if fallback.is_file():
            return FileResponse(fallback)
        raise HTTPException(404, 'Frontend build not found — run `bun run build` in packages/frontend')


app = create_app()
