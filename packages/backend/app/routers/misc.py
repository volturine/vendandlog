from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.deps import acting_as, current_user
from app.models import Conversation, Flag, Listing, Rating, User
from app.readers import user_public

router = APIRouter(prefix='/api', tags=['misc'])


class RateBody(BaseModel):
    listing_id: int
    stars: int
    text: str = ''


class FlagBody(BaseModel):
    handle: str
    reason: str


@router.get('/health')
def health() -> dict:
    return {'status': 'ok'}


@router.get('/me')
def me(request: Request, session: Session = Depends(get_session)) -> dict | None:
    user = current_user(request, session)
    if user is None:
        return None
    result = user_public(session, user.handle)
    assert result is not None
    return result


@router.post('/ratings')
def rate(body: RateBody, request: Request, session: Session = Depends(get_session)) -> dict:
    """Two-sided trust: after a sale, each side rates the other. Once."""
    handle = acting_as(request, session=session)
    listing = session.get(Listing, body.listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {body.listing_id}')
    if listing.status != 'sold':
        raise HTTPException(409, 'Ratings unlock when the listing is sold')
    if handle == listing.seller_handle:
        ratee = _buyer_of(session, listing.id)
    else:
        was_participant = session.exec(select(Conversation).where(Conversation.listing_id == listing.id, Conversation.buyer_handle == handle)).first()
        if not was_participant:
            raise HTTPException(403, 'Only the seller or a buyer of this listing may rate')
        ratee = listing.seller_handle
    if ratee is None:
        raise HTTPException(409, 'No counterparty to rate')
    if not 1 <= body.stars <= 5:
        raise HTTPException(422, 'Stars must be 1..5')
    existing = session.exec(
        select(Rating).where(
            Rating.listing_id == listing.id,
            Rating.rater_handle == handle,
            Rating.ratee_handle == ratee,
        )
    ).first()
    if existing:
        raise HTTPException(409, f'You already rated @{ratee} for this listing')
    rating = Rating(
        listing_id=listing.id,
        rater_handle=handle,
        ratee_handle=ratee,
        stars=body.stars,
        text=body.text,
    )
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return {
        'id': rating.id,
        'listing_id': rating.listing_id,
        'rater_handle': rating.rater_handle,
        'ratee_handle': rating.ratee_handle,
        'stars': rating.stars,
        'text': rating.text,
        'created_at': rating.created_at,
    }


def _buyer_of(session: Session, listing_id: int) -> str | None:
    conversation = session.exec(select(Conversation).where(Conversation.listing_id == listing_id)).first()
    return conversation.buyer_handle if conversation else None


@router.post('/flags')
def flag(body: FlagBody, request: Request, session: Session = Depends(get_session)) -> dict:
    """Highlight scammers. Skeleton: flags auto-upheld and visible on the profile."""
    reporter = acting_as(request, session=session)
    if reporter == body.handle:
        raise HTTPException(409, 'You cannot flag yourself')
    if user_public(session, body.handle) is None:
        raise HTTPException(404, f'No user {body.handle}')
    target = session.get(User, body.handle)
    assert target is not None
    target.flags_upheld += 1
    flag = Flag(reporter_handle=reporter, target_handle=body.handle, reason=body.reason, upheld=True)
    session.add(flag)
    session.add(target)
    session.commit()
    return {'ok': True}
