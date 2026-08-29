from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.deps import acting_as
from app.events import append_event
from app.models import Conversation, Listing, Message, User
from app.readers import conversation_is_public, conversation_public, user_public

router = APIRouter(prefix='/api', tags=['conversations'])


class OpenConversation(BaseModel):
    body: str | None = None


class SendMessage(BaseModel):
    body: str


def _conversation_or_403(session: Session, conversation_id: int, handle: str | None) -> tuple[Conversation, Listing]:
    conversation = session.get(Conversation, conversation_id)
    if conversation is None:
        raise HTTPException(404, f'No conversation {conversation_id}')
    listing = session.get(Listing, conversation.listing_id)
    assert listing is not None
    participant = handle in {conversation.buyer_handle, listing.seller_handle}
    if not conversation_is_public(session, conversation, listing) and not participant:
        raise HTTPException(403, 'This conversation is private — it becomes public when the listing sells')
    return conversation, listing


@router.post('/listings/{listing_id}/conversations')
def start_conversation(listing_id: int, body: OpenConversation, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = acting_as(request)
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    if listing.seller_handle == handle:
        raise HTTPException(409, 'Sellers cannot open conversations with themselves')
    if listing.status == 'sold':
        raise HTTPException(409, 'Listing already sold — read the public record instead')
    if user_public(session, handle) is None:
        raise HTTPException(401, f'Unknown actor {handle}')

    existing = session.exec(select(Conversation).where(Conversation.listing_id == listing_id, Conversation.buyer_handle == handle)).first()
    if existing:
        conversation = existing
    else:
        conversation = Conversation(listing_id=listing_id, buyer_handle=handle)
        session.add(conversation)
        session.flush()

    if body.body:
        message = Message(conversation_id=conversation.id, author_handle=handle, body=body.body)
        session.add(message)
    session.commit()
    result = conversation_public(session, conversation)
    assert result is not None
    return result


@router.get('/listings/{listing_id}/conversations')
def listing_conversations(listing_id: int, request: Request, session: Session = Depends(get_session)) -> list[dict]:
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, f'No listing {listing_id}')
    handle = request.headers.get('X-Acting-As')
    rows = session.exec(select(Conversation).where(Conversation.listing_id == listing_id)).all()
    view = []
    for conversation in rows:
        participant = handle in {conversation.buyer_handle, listing.seller_handle}
        if conversation_is_public(session, conversation, listing) or participant:
            serialized = conversation_public(session, conversation)
            if serialized:
                view.append(serialized)
    return view


@router.get('/conversations/{conversation_id}')
def get_conversation(conversation_id: int, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = request.headers.get('X-Acting-As')
    conversation, _listing = _conversation_or_403(session, conversation_id, handle)
    result = conversation_public(session, conversation)
    assert result is not None
    messages = session.exec(select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)).all()
    names = {u.handle: u.name for u in session.exec(select(User)).all()}
    result['messages'] = [
        {
            'id': m.id,
            'author_handle': m.author_handle,
            'author_name': names.get(m.author_handle, m.author_handle),
            'body': m.body,
            'created_at': m.created_at,
        }
        for m in messages
    ]
    return result


@router.post('/conversations/{conversation_id}/messages')
def send_message(conversation_id: int, body: SendMessage, request: Request, session: Session = Depends(get_session)) -> dict:
    handle = acting_as(request)
    conversation, listing = _conversation_or_403(session, conversation_id, handle)
    if handle not in {conversation.buyer_handle, listing.seller_handle}:
        raise HTTPException(403, 'Only the buyer or seller may write here')
    if listing.status == 'sold':
        raise HTTPException(409, 'Listing sold — the conversation is now read-only public record')
    message = Message(conversation_id=conversation_id, author_handle=handle, body=body.body)
    session.add(message)
    session.commit()
    session.refresh(message)
    return {
        'id': message.id,
        'author_handle': handle,
        'author_name': handle,
        'body': message.body,
        'created_at': message.created_at,
    }


@router.post('/conversations/{conversation_id}/unhide')
def unhide_conversation(conversation_id: int, request: Request, session: Session = Depends(get_session)) -> dict:
    """Either party may prematurely make the conversation public. Logged on the listing record."""
    handle = acting_as(request)
    conversation, listing = _conversation_or_403(session, conversation_id, handle)
    if handle not in {conversation.buyer_handle, listing.seller_handle}:
        raise HTTPException(403, 'Only a participant may unhide this conversation')
    if not conversation.is_public:
        conversation.is_public = True
        conversation.unhidden_by = handle
        session.add(conversation)
        append_event(
            session,
            listing,
            'conversation_public',
            'Conversation unhidden early',
            f'at the request of @{handle} — before any sale',
        )
        session.commit()
    result = conversation_public(session, conversation)
    assert result is not None
    return result
