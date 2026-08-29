from datetime import UTC, datetime

from sqlmodel import Session, select

from app.domain import GENESIS, event_hash
from app.models import Listing, ListingEvent


def append_event(
    session: Session,
    listing: Listing,
    kind: str,
    summary: str,
    detail: str | None = None,
) -> ListingEvent:
    """Append to the immutable log. The chain commits each entry to its predecessor."""
    previous = session.exec(
        select(ListingEvent).where(ListingEvent.listing_id == listing.id).order_by(ListingEvent.created_at.desc(), ListingEvent.id.desc())
    ).first()
    prev_hash = previous.hash if previous else GENESIS
    created_at = datetime.now(UTC).isoformat()
    event = ListingEvent(
        listing_id=listing.id,
        kind=kind,
        summary=summary,
        detail=detail,
        hash=event_hash(prev_hash, listing.id, kind, summary, detail, created_at),
        created_at=created_at,
    )
    session.add(event)
    listing.updated_at = created_at
    session.add(listing)
    session.flush()
    return event
