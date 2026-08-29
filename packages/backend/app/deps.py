from fastapi import HTTPException, Request
from sqlmodel import Session

from app.models import AuthSession, User

COOKIE_NAME = 'vdl_session'


def current_user(request: Request, session: Session) -> User | None:
    """The signed-in user, or None. Resolved from the session cookie."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    auth_session = session.get(AuthSession, token)
    if auth_session is None:
        return None
    return session.get(User, auth_session.user_handle)


def acting_handle(request: Request, session: Session) -> str | None:
    user = current_user(request, session)
    return user.handle if user else None


def acting_as(request: Request, session: Session) -> str:
    """Endpoints that require an identity raise 401 without one."""
    handle = acting_handle(request, session)
    if not handle:
        raise HTTPException(401, 'Sign in required')
    return handle
