from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


def utcnow() -> str:
    return datetime.now(UTC).isoformat()


class Condition(StrEnum):
    like_new = 'like_new'
    good = 'good'
    fair = 'fair'


class ListingStatus(StrEnum):
    active = 'active'
    sold = 'sold'
    withdrawn = 'withdrawn'


class User(SQLModel, table=True):
    handle: str = Field(primary_key=True)
    name: str
    bio: str = ''
    avatar_color: str = '#c6b3f2'
    created_at: str = Field(default_factory=utcnow)
    verified: bool = False
    flags_upheld: int = 0


class Listing(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    price_cents: int
    previous_price_cents: int | None = None
    condition: Condition = Condition.good
    status: ListingStatus = ListingStatus.active
    category: str = 'other'
    location: str = ''
    image_url: str | None = None
    seller_handle: str = Field(foreign_key='user.handle')
    created_at: str = Field(default_factory=utcnow)
    updated_at: str = Field(default_factory=utcnow)
    sold_at: str | None = None


class ListingEvent(SQLModel, table=True):
    """Append-only. Never updated, never deleted — this is the product."""

    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key='listing.id', index=True)
    kind: str  # listed | price_drop | description_edited | sold | ...
    summary: str
    detail: str | None = None
    hash: str
    created_at: str = Field(default_factory=utcnow, index=True)


class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key='listing.id', index=True)
    buyer_handle: str = Field(foreign_key='user.handle')
    is_public: bool = False
    unhidden_by: str | None = None
    created_at: str = Field(default_factory=utcnow)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key='conversation.id', index=True)
    author_handle: str = Field(foreign_key='user.handle')
    body: str
    created_at: str = Field(default_factory=utcnow, index=True)


class Rating(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key='listing.id', index=True)
    rater_handle: str = Field(foreign_key='user.handle')
    ratee_handle: str = Field(foreign_key='user.handle', index=True)
    stars: int  # 1..5
    text: str = ''
    created_at: str = Field(default_factory=utcnow)


class Flag(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    reporter_handle: str = Field(foreign_key='user.handle')
    target_handle: str = Field(foreign_key='user.handle', index=True)
    reason: str
    upheld: bool = True  # skeleton: auto-upheld; moderation is future work
    created_at: str = Field(default_factory=utcnow)
