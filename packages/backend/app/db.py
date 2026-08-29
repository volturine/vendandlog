import os
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings


def _create_engine():
    url = get_settings().db_url
    if url.startswith('sqlite'):
        return create_engine(url, connect_args={'check_same_thread': False})
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5)


engine = _create_engine()


def init_db() -> None:
    """Test/dev convenience (SQLite only): create everything from metadata.

    Real schema evolution happens through Alembic (see run_migrations).
    """
    from app import models  # noqa: F401  (register tables)

    SQLModel.metadata.create_all(engine)


def run_migrations() -> None:
    """Apply Alembic migrations (production path: Postgres)."""
    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parents[1]
    alembic_cfg = Config(str(root / 'alembic.ini'))
    alembic_cfg.set_main_option('script_location', str(root / 'migrations'))
    alembic_cfg.set_main_option('sqlalchemy.url', get_settings().db_url)
    os.environ.setdefault('VDL_DB_URL', get_settings().db_url)
    command.upgrade(alembic_cfg, 'head')


def get_session():
    with Session(engine) as session:
        yield session
