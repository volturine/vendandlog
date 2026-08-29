"""Read-side serializers. Plain dicts on purpose: one shape, shared with the frontend contract."""

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.domain import positive_pct, trust_score
from app.models import Conversation, Listing, ListingEvent, Message, Rating, User

SEED_NOW = None  # tests inject nothing; seeds use real clock offsets


def iso(dt: datetime) -> str:
    return dt.isoformat()


def hours_ago(h: float) -> str:
    from datetime import timedelta

    return iso(datetime.now(UTC) - timedelta(hours=h))


def user_public(session: Session, handle: str) -> dict | None:
    user = session.get(User, handle)
    if not user:
        return None
    ratings = list(session.exec(select(Rating).where(Rating.ratee_handle == handle)).all())
    stars = [r.stars for r in ratings]
    sales = list(session.exec(select(Listing).where(Listing.seller_handle == handle, Listing.status == 'sold')).all())
    return {
        'handle': user.handle,
        'name': user.name,
        'bio': user.bio,
        'avatar_color': user.avatar_color,
        'created_at': user.created_at,
        'verified': user.verified,
        'flags_upheld': user.flags_upheld,
        'sales_count': len(sales),
        'trust_score': trust_score(len(sales), stars, user.flags_upheld, _listings_count(session, handle)),
        'positive_pct': positive_pct(stars),
    }


def _listings_count(session: Session, handle: str) -> int:
    return len(list(session.exec(select(Listing).where(Listing.seller_handle == handle)).all()))


def listing_public(session: Session, listing: Listing) -> dict | None:
    seller = user_public(session, listing.seller_handle)
    if seller is None:
        return None
    events = list(session.exec(select(ListingEvent).where(ListingEvent.listing_id == listing.id).order_by(ListingEvent.created_at.desc())).all())
    conversations = list(session.exec(select(Conversation).where(Conversation.listing_id == listing.id)).all())
    public_count = sum(1 for c in conversations if conversation_is_public(session, c, listing))
    mine = 0  # filled by callers that know the actor
    last = events[0] if events else None
    return {
        'id': listing.id,
        'title': listing.title,
        'description': listing.description,
        'price_cents': listing.price_cents,
        'previous_price_cents': listing.previous_price_cents,
        'condition': listing.condition,
        'status': listing.status,
        'category': listing.category,
        'location': listing.location,
        'image_url': listing.image_url,
        'seller': seller,
        'created_at': listing.created_at,
        'updated_at': listing.updated_at,
        'sold_at': listing.sold_at,
        'event_count': len(events),
        'last_event': ({'kind': last.kind, 'summary': last.summary, 'created_at': last.created_at} if last else None),
        'public_conversation_count': public_count,
        'open_conversation_count': max(0, len(conversations) - public_count),
        '_open_mine': mine,
    }


def conversation_is_public(session: Session, conversation: Conversation, listing: Listing) -> bool:
    """The invariant: sold means public. Either party may also unhide early."""
    return conversation.is_public or listing.status == 'sold'


def conversation_public(session: Session, conversation: Conversation) -> dict | None:
    listing = session.get(Listing, conversation.listing_id)
    buyer = user_public(session, conversation.buyer_handle)
    if listing is None or buyer is None:
        return None
    messages = list(session.exec(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)).all())
    last_at = messages[-1].created_at if messages else conversation.created_at
    return {
        'id': conversation.id,
        'listing_id': conversation.listing_id,
        'buyer_handle': conversation.buyer_handle,
        'buyer_name': buyer['name'],
        'is_public': conversation_is_public(session, conversation, listing),
        'created_at': conversation.created_at,
        'message_count': len(messages),
        'last_message_at': last_at,
    }
