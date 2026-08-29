from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import User
from app.readers import user_public

router = APIRouter(prefix='/api/users', tags=['users'])


@router.get('')
def list_users(session: Session = Depends(get_session)) -> list[dict]:
    users = session.exec(select(User)).all()
    return [u for u in (user_public(session, user.handle) for user in users) if u]


@router.get('/{handle}')
def get_user(handle: str, session: Session = Depends(get_session)) -> dict:
    user = user_public(session, handle)
    if user is None:
        raise HTTPException(404, f'No user {handle}')
    return user


@router.get('/{handle}/listings')
def get_user_listings(handle: str, session: Session = Depends(get_session)) -> list[dict]:
    if user_public(session, handle) is None:
        raise HTTPException(404, f'No user {handle}')
    from app.models import Listing
    from app.readers import listing_public

    listings = session.exec(select(Listing).where(Listing.seller_handle == handle).order_by(Listing.updated_at.desc())).all()
    return [item for item in (listing_public(session, listing) for listing in listings) if item]


@router.get('/{handle}/ratings')
def get_user_ratings(handle: str, direction: str = 'received', session: Session = Depends(get_session)) -> list[dict]:
    from app.models import Rating

    if user_public(session, handle) is None:
        raise HTTPException(404, f'No user {handle}')
    column = Rating.ratee_handle if direction == 'received' else Rating.rater_handle
    ratings = session.exec(select(Rating).where(column == handle).order_by(Rating.created_at.desc())).all()
    return [
        {
            'id': r.id,
            'listing_id': r.listing_id,
            'rater_handle': r.rater_handle,
            'ratee_handle': r.ratee_handle,
            'stars': r.stars,
            'text': r.text,
            'created_at': r.created_at,
        }
        for r in ratings
    ]
