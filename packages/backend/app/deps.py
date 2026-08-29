from fastapi import HTTPException, Request

from app.db import get_session  # noqa: F401  (re-export for routers)


def acting_as(request: Request) -> str:
    """Skeleton auth: the client declares who acts via X-Acting-As.

    Real auth (passkeys/OIDC) is future work; the API shape will not change.
    """
    handle = request.headers.get('X-Acting-As')
    if not handle:
        raise HTTPException(401, 'Missing X-Acting-As header — pick an identity first')
    return handle
