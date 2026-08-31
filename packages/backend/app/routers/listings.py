from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.deps import acting_as, acting_handle
from app.events import append_event
from app.models import Condition, Listing, ListingEvent, ListingStatus
from app.readers import listing_public, user_public

router = APIRouter(prefix='/api/listings', tags=['listings'])


class CreateListing(BaseModel):
    title: str
    description: str
    price: float
    condition: Condition = Condition.good
    category: str = 'other'
    location: str = ''
    image_url: str | None = None


class UpdateListing(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    location: str | None = None


class StatusChange(BaseModel):
    action: ListingStatus


@router.get('')
def browse(
    q: str | None = None,
    category: str | None = None,
    status: str = 'active',
    sort: str = 'recent',
    session: Session = Depends(get_session),
) -> list[dict]:
    query = select(Listing)
    if status != 'all':
        query = query.where(Listing.status == status)
    if category:
        query = query.where(Listing.category == category)
    if q:
        like = f'%{q}%'
        query = query.where(Listing.title.ilike(like) | Listing.description.ilike(like))
    order = {
        'recent': Listing.updated_at.desc(),
        'price_asc': Listing.price_cents.asc(),
        'price_desc': Listing.price_cents.desc(),
        'events': Listing.created_at.desc(),
    }
    listings = session.exec(query.order_by(order.get(sort, order['recent']))).all()
    result = [item for item in (listing_public(session, listing) for listing in listings) if item]
    if sort == 'events':
        result.sort(key=lambda entry: entry['event_count'], reverse=True)
    return result


@router.post('')
def create_listing(body: CreateListing, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = acting_as(request, session=session)
    if user_public(session, handle) is None:
        raise HTTPException(401, f'Unknown actor {handle}')
    price_cents = round(body.price * 100)
    listing = Listing(
        title=body.title,
        description=body.description,
        price_cents=price_cents,
        condition=body.condition,
        category=body.category,
        location=body.location,
        image_url=body.image_url,
        seller_handle=handle,
    )
    session.add(listing)
    session.flush()
    append_event(session, listing, 'listed', f'Listed — {body.title}', f'ask ${body.price:g}')
    session.commit()
    session.refresh(listing)
    result = listing_public(session, listing)
    assert result is not None
    return result


@router.get('/{listing_id}')
def get_listing(listing_id: int, request: Request, session: Session = Depends(get_session)) -> dict:
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    actor = acting_handle(request, session=session)
    result = listing_public(session, listing)
    assert result is not None
    events = session.exec(select(ListingEvent).where(ListingEvent.listing_id == listing_id).order_by(ListingEvent.created_at.desc())).all()
    result['events'] = [
        {
            'id': e.id,
            'listing_id': e.listing_id,
            'kind': e.kind,
            'summary': e.summary,
            'detail': e.detail,
            'hash': e.hash,
            'created_at': e.created_at,
        }
        for e in events
    ]
    result['conversations'] = _conversations_view(session, listing, actor)
    result['similar'] = _similar(session, listing)
    result['my_rating'] = _my_rating(session, listing, actor)
    return result


def _my_rating(session: Session, listing: Listing, actor: str | None) -> dict | None:
    """The actor's outgoing rating for this listing, if any (drives the rate UI)."""
    from app.models import Rating

    if not actor:
        return None
    rating = session.exec(select(Rating).where(Rating.listing_id == listing.id, Rating.rater_handle == actor)).first()
    if not rating:
        return None
    return {
        'id': rating.id,
        'stars': rating.stars,
        'text': rating.text,
        'ratee_handle': rating.ratee_handle,
        'created_at': rating.created_at,
    }


def _conversations_view(session: Session, listing: Listing, actor: str | None) -> list[dict]:
    """Public conversations for everyone; the actor also sees their own."""
    from app.models import Conversation
    from app.readers import conversation_is_public, conversation_public

    view: list[dict] = []
    for conversation in session.exec(select(Conversation).where(Conversation.listing_id == listing.id)).all():
        participant = actor in {conversation.buyer_handle, listing.seller_handle}
        if conversation_is_public(session, conversation, listing) or participant:
            serialized = conversation_public(session, conversation)
            if serialized is not None:
                view.append(serialized)
    return view


def _similar(session: Session, listing: Listing) -> list[dict]:
    others = session.exec(
        select(Listing)
        .where(Listing.category == listing.category, Listing.id != listing.id, Listing.status == 'active')
        .order_by(Listing.updated_at.desc())
        .limit(3)
    ).all()
    return [item for item in (listing_public(session, other) for other in others) if item]


@router.patch('/{listing_id}')
def update_listing(listing_id: int, body: UpdateListing, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = acting_as(request, session=session)
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    if listing.seller_handle != handle:
        raise HTTPException(403, 'Only the seller may edit this listing')
    if listing.status == 'sold':
        raise HTTPException(409, 'Sold listings are part of the record — edits are not allowed')

    changes: list[str] = []
    if body.price is not None and round(body.price * 100) != listing.price_cents:
        old = listing.price_cents
        listing.previous_price_cents = old
        listing.price_cents = round(body.price * 100)
        direction = 'price_drop' if listing.price_cents < old else 'price_raise'
        append_event(
            session,
            listing,
            direction,
            f'Price changed ${old / 100:g} → ${listing.price_cents / 100:g}',
            'edit via listing form',
        )
        changes.append('price')
    if body.title is not None and body.title != listing.title:
        listing.title = body.title
        changes.append('title')
    if body.description is not None and body.description != listing.description:
        listing.description = body.description
        append_event(session, listing, 'description_edited', 'Description edited', 'diff public')
        changes.append('description')
    if body.location is not None and body.location != listing.location:
        listing.location = body.location
        changes.append('location')
    if not changes:
        raise HTTPException(422, 'Nothing to change')
    if 'title' in changes:
        append_event(session, listing, 'description_edited', f'Title edited → “{listing.title}”')
    session.commit()
    session.refresh(listing)
    result = listing_public(session, listing)
    assert result is not None
    return result


@router.post('/{listing_id}/status')
def change_status(listing_id: int, body: StatusChange, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = acting_as(request, session=session)
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    if listing.seller_handle != handle:
        raise HTTPException(403, 'Only the seller may change the status')

    from datetime import UTC, datetime

    if body.action == 'sold':
        if listing.status == 'sold':
            raise HTTPException(409, 'Already sold')
        listing.status = 'sold'
        listing.sold_at = datetime.now(UTC).isoformat()
        append_event(
            session,
            listing,
            'sold',
            'Sold — conversations with buyers are now public',
        )
    elif body.action == 'withdrawn':
        if listing.status == 'withdrawn':
            raise HTTPException(409, 'Already withdrawn')
        listing.status = 'withdrawn'
        append_event(session, listing, 'withdrawn', 'Withdrawn — stays public, per the record')
    else:
        if listing.status != 'withdrawn':
            raise HTTPException(409, 'Only withdrawn listings can be relisted')
        listing.status = 'active'
        listing.sold_at = None
        append_event(session, listing, 'relisted', 'Relisted')
    session.commit()
    session.refresh(listing)
    result = listing_public(session, listing)
    assert result is not None
    return result


@router.get('/{listing_id}/events')
def listing_events(listing_id: int, session: Session = Depends(get_session)) -> list[dict]:
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    events = session.exec(select(ListingEvent).where(ListingEvent.listing_id == listing_id).order_by(ListingEvent.created_at.desc())).all()
    return [
        {
            'id': e.id,
            'listing_id': e.listing_id,
            'kind': e.kind,
            'summary': e.summary,
            'detail': e.detail,
            'hash': e.hash,
            'created_at': e.created_at,
        }
        for e in events
    ]
