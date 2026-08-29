import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.deps import COOKIE_NAME
from app.models import AuthSession, User
from app.passwords import hash_password, new_session_token, verify_password
from app.readers import user_public

router = APIRouter(prefix='/api/auth', tags=['auth'])

HANDLE_RE = re.compile(r'^[a-z0-9][a-z0-9._-]{1,31}$')
SESSION_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


class Credentials(BaseModel):
    handle: str
    password: str


class Registration(Credentials):
    name: str


def _start_session(response: Response, session: Session, handle: str) -> None:
    token = new_session_token()
    session.add(AuthSession(token=token, user_handle=handle))
    response.set_cookie(COOKIE_NAME, token, httponly=True, samesite='lax', max_age=SESSION_MAX_AGE, path='/')


@router.post('/register')
def register(body: Registration, response: Response, session: Session = Depends(get_session)) -> dict:
    handle = body.handle.strip().lower()
    if not HANDLE_RE.fullmatch(handle):
        raise HTTPException(422, 'Handle must be 2-32 chars: lowercase letters, digits, dots, dashes, underscores')
    if not body.name.strip():
        raise HTTPException(422, 'Name is required')
    if len(body.password) < 4:
        raise HTTPException(422, 'Password must be at least 4 characters')
    if session.get(User, handle):
        raise HTTPException(409, f'Handle @{handle} is taken')

    user = User(handle=handle, name=body.name.strip(), password_hash=hash_password(body.password))
    session.add(user)
    session.flush()
    _start_session(response, session, handle)
    session.commit()
    result = user_public(session, handle)
    assert result is not None
    return result


@router.post('/login')
def login(body: Credentials, response: Response, session: Session = Depends(get_session)) -> dict:
    handle = body.handle.strip().lower()
    user = session.get(User, handle)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, 'Wrong handle or password')
    _start_session(response, session, handle)
    session.commit()
    result = user_public(session, handle)
    assert result is not None
    return result


@router.post('/logout')
def logout(request: Request, response: Response, session: Session = Depends(get_session)) -> dict:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        stored = session.get(AuthSession, token)
        if stored:
            session.delete(stored)
            session.commit()
    response.delete_cookie(COOKIE_NAME, path='/')
    return {'ok': True}
