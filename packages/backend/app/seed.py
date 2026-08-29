"""Demo data. Runs once on an empty database; gives every screen something honest to show."""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.db import engine
from app.domain import GENESIS, event_hash
from app.models import Condition, Conversation, Listing, ListingEvent, Message, Rating, User


def _ago(hours: float) -> str:
    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


def _event(session: Session, listing: Listing, kind: str, summary: str, detail: str | None, hours: float) -> None:
    previous = session.exec(select(ListingEvent).where(ListingEvent.listing_id == listing.id).order_by(ListingEvent.id.desc())).first()
    prev_hash = previous.hash if previous else GENESIS
    created_at = _ago(hours)
    session.add(
        ListingEvent(
            listing_id=listing.id,
            kind=kind,
            summary=summary,
            detail=detail,
            hash=event_hash(prev_hash, listing.id, kind, summary, detail, created_at),
            created_at=created_at,
        )
    )


def ensure_seeded() -> None:
    with Session(engine) as session:
        if session.exec(select(User)).first():
            return
        _seed(session)
        session.commit()


def _users() -> list[User]:
    """Fresh instances on every call — reused model objects would be no-ops in a new session."""
    return [
        User(
            handle='jana.b',
            name='Jana Bergmann',
            bio='Bikes, mostly. I meet at Radhaus so your mechanic can check everything.',
            avatar_color='#98e9d9',
            verified=True,
            created_at=_ago(24 * 900),
        ),
        User(handle='lea_rides', name='Lea Richter', bio='Selling what I ride.', avatar_color='#b3e2a1', verified=True, created_at=_ago(24 * 1200)),
        User(handle='marat_77', name='Marat K.', bio='First listing here — be gentle.', avatar_color='#f6aea0', created_at=_ago(24 * 20)),
        User(handle='gravelgus', name='Gustav Lange', bio='Gravel everywhere.', avatar_color='#a9d5f4', created_at=_ago(24 * 400)),
        User(
            handle='cityhop', name='City Hop Bikes', bio='Small shop, second-hand commuters.', avatar_color='#f7d875', verified=True, created_at=_ago(24 * 800)
        ),
        User(handle='tomsfamily', name='Tom H.', bio='Family clearing the basement.', avatar_color='#f9c2d8', created_at=_ago(24 * 200)),
        User(
            handle='byte_berlin',
            name='Byte Berlin',
            bio='Refurbished laptops with battery receipts.',
            avatar_color='#c6b3f2',
            verified=True,
            created_at=_ago(24 * 700),
        ),
        User(handle='stringsnthings', name='Sofia M.', bio='Guitars loved and played.', avatar_color='#d6c5b0', created_at=_ago(24 * 350)),
        User(handle='milan', name='Milan G.', bio='Mostly buying.', avatar_color='#98e9d9', created_at=_ago(24 * 500)),
    ]


def _seed(session: Session) -> None:
    for user in _users():
        session.add(user)
    session.flush()

    def add(listing: Listing) -> Listing:
        session.add(listing)
        session.flush()
        return listing

    canyon = add(
        Listing(
            title='Canyon Endurace AL 7.0 — 54cm, carbon fork, recent tune',
            description=(
                'Ridden two seasons, mostly flat commutes. Recent full tune-up at Radhaus (receipt in photos) — '
                'new cassette, chain and bar tape. Carbon fork, no crashes, one small paint chip on the '
                'drive-side chainstay. Happy to meet at a bike shop so a mechanic can look it over.'
            ),
            price_cents=34000,
            previous_price_cents=41000,
            condition=Condition.like_new,
            category='bikes',
            location='Kreuzberg · 2 km',
            image_url='https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='jana.b',
            created_at=_ago(120),
        )
    )
    _event(session, canyon, 'listed', 'Listed — Canyon Endurace AL 7.0', 'ask $420', 120)
    _event(session, canyon, 'description_edited', 'Description edited — added service history', 'diff public', 72)
    _event(session, canyon, 'verified', 'Verified — serial number checked against bike registry', None, 71)
    _event(session, canyon, 'photo_added', 'Photo added — tune-up receipt', None, 50)
    _event(session, canyon, 'price_drop', 'Price dropped — $410 → $340', 'negotiation with @milan', 48)

    cube = add(
        Listing(
            title='Cube Attention MTB, size M — new chain + brake pads',
            description='Sold within a week. Full negotiation history below — read it before you buy anything from anyone.',
            price_cents=27500,
            condition=Condition.good,
            category='bikes',
            location='Friedrichshain · 7 km',
            image_url='https://images.unsplash.com/photo-1571068316344-75bc76f77890?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='lea_rides',
            created_at=_ago(24 * 14),
            sold_at=_ago(24 * 6),
        )
    )
    cube.status = 'sold'
    _event(session, cube, 'listed', 'Listed — Cube Attention MTB', 'ask $290', 24 * 14)
    _event(session, cube, 'price_drop', 'Price dropped — $290 → $275', None, 24 * 9)
    _event(session, cube, 'sold', 'Sold — conversations with buyers are now public', None, 24 * 6)

    ribble = add(
        Listing(
            title='Ribble CGR AL — gravel, Shimano GRX, 200 km total',
            description=(
                'Bought last spring, ridden 200 gentle km. GRX 400 groupset, tubeless. Selling because a knee '
                'injury means more road, less gravel. Happy to show any receipt.'
            ),
            price_cents=89000,
            condition=Condition.like_new,
            category='bikes',
            location='Prenzlauer Berg · 3 km',
            image_url='https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='gravelgus',
            created_at=_ago(0.5),
        )
    )
    _event(session, ribble, 'listed', 'Listed — Ribble CGR AL', 'matched 4 wishlists', 0.5)

    peugeot = add(
        Listing(
            title='Vintage Peugeot road bike — single-speed conversion',
            description='80s frame, converted to single speed. Rides nicely, some paint wear. First listing here.',
            price_cents=12000,
            condition=Condition.good,
            category='bikes',
            location='Neukölln · 4 km',
            image_url='https://images.unsplash.com/photo-1507035895480-2b3156c31fc8?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='marat_77',
            created_at=_ago(1),
        )
    )
    _event(session, peugeot, 'listed', 'Listed — Vintage Peugeot single-speed', None, 1)

    touring = add(
        Listing(
            title='Touring bike with panniers — fully serviced, ready to ride',
            description='Steel tourer with front and rear racks, two Ortlieb panniers included. New tyres, new bottom bracket this spring.',
            price_cents=15000,
            previous_price_cents=18000,
            condition=Condition.good,
            category='bikes',
            location='Mitte · 1 km',
            image_url='https://images.unsplash.com/photo-1511994298241-608e28f14fde?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='cityhop',
            created_at=_ago(30),
        )
    )
    _event(session, touring, 'listed', 'Listed — touring bike with panniers', 'ask $180', 30)
    _event(session, touring, 'price_drop', 'Price dropped — $180 → $150', 'after negotiation, reason public', 5)

    citybike = add(
        Listing(
            title='City bike 28" — basket and lights included',
            description='Honest condition: some rust on the chain guard, everything works. Good first bike.',
            price_cents=6000,
            condition=Condition.fair,
            category='bikes',
            location='Wedding · 6 km',
            image_url='https://images.unsplash.com/photo-1505705694340-019e1e335916?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='tomsfamily',
            created_at=_ago(3),
        )
    )
    _event(session, citybike, 'listed', 'Listed — city bike 28"', '2 photos, honest rust note', 3)

    macbook = add(
        Listing(
            title='MacBook Air M1 8/256 — battery 92%, AppleCare till 2026',
            description='Refurbished by us, battery report and AppleCare documents included. Meet at the shop so you can test everything.',
            price_cents=62000,
            previous_price_cents=70000,
            condition=Condition.good,
            category='electronics',
            location='Mitte · 1 km',
            image_url='https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='byte_berlin',
            created_at=_ago(24 * 5),
        )
    )
    _event(session, macbook, 'listed', 'Listed — MacBook Air M1', 'ask $700', 24 * 5)
    _event(session, macbook, 'price_drop', 'Price dropped — $700 → $620', 'negotiation public', 24 * 2)

    tele = add(
        Listing(
            title='Fender Telecaster MIM — new strings, gig bag',
            description='Mexican-made Tele, 2018. Few honest scratches, plays great. New strings, includes padded gig bag.',
            price_cents=45000,
            condition=Condition.good,
            category='instruments',
            location='Mitte · 1 km',
            image_url='https://images.unsplash.com/photo-1510915361894-db8b60106cb1?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='stringsnthings',
            created_at=_ago(4),
        )
    )
    _event(session, tele, 'listed', 'Listed — Fender Telecaster MIM', None, 4)
    _event(session, tele, 'description_edited', 'Note added — restring included', None, 4)

    sofa = add(
        Listing(
            title='Olive wool three-seat sofa — photos of every seam',
            description='Sturdy sofa from a smoke-free, pet-free home. One cushion has a faint sun fade — pictured.',
            price_cents=24000,
            condition=Condition.good,
            category='furniture',
            location='Schöneberg · 5 km',
            image_url='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='cityhop',
            created_at=_ago(26),
        )
    )
    _event(session, sofa, 'listed', 'Listed — olive wool sofa', None, 26)
    _event(session, sofa, 'photo_added', 'Photos added — fabric close-ups', None, 24)

    session.flush()

    # Conversation on the sold listing: public because of the sale.
    conv_cube = Conversation(listing_id=cube.id, buyer_handle='milan', is_public=False, created_at=_ago(24 * 10))
    session.add(conv_cube)
    session.flush()
    session.add(Message(conversation_id=conv_cube.id, author_handle='milan', body='Hi! Any rust on the frame? Photos look clean.', created_at=_ago(24 * 10)))
    session.add(
        Message(
            conversation_id=conv_cube.id,
            author_handle='lea_rides',
            body='Only surface rust on the bottle cage bolts, shown in photo 4. Happy to swap them for new ones.',
            created_at=_ago(24 * 10 + 1),
        )
    )
    session.add(
        Message(
            conversation_id=conv_cube.id,
            author_handle='milan',
            body='Deal at $275 if you include the swap. Meet at the U-Bahn station?',
            created_at=_ago(24 * 9),
        )
    )

    # Open (private) conversation on the canyon.
    conv_canyon = Conversation(listing_id=canyon.id, buyer_handle='milan', is_public=False, created_at=_ago(49))
    session.add(conv_canyon)
    session.flush()
    session.add(Message(conversation_id=conv_canyon.id, author_handle='milan', body='Would you take $340? I can pick up tomorrow.', created_at=_ago(49)))
    session.add(
        Message(conversation_id=conv_canyon.id, author_handle='jana.b', body='$340 works if we meet at Radhaus — receipt is there too.', created_at=_ago(48))
    )

    session.flush()

    # Older sales so trust history feels lived-in: jana has two prior sales with ratings.
    brompton = add(
        Listing(
            title='Brompton M3L folding bike — commuter classic',
            description='Folding commuter, everything works. Sold quickly — full history below.',
            price_cents=34000,
            condition=Condition.good,
            category='bikes',
            location='Kreuzberg · 2 km',
            image_url='https://images.unsplash.com/photo-1502744688674-c619d1586c9e?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='jana.b',
            created_at=_ago(24 * 34),
            sold_at=_ago(24 * 30),
        )
    )
    brompton.status = 'sold'
    _event(session, brompton, 'listed', 'Listed — Brompton M3L', 'ask $360', 24 * 34)
    _event(session, brompton, 'sold', 'Sold — conversations with buyers are now public', None, 24 * 30)

    conv_brompton = Conversation(listing_id=brompton.id, buyer_handle='tomsfamily', is_public=False, created_at=_ago(24 * 32))
    session.add(conv_brompton)
    session.flush()
    session.add(Message(conversation_id=conv_brompton.id, author_handle='tomsfamily', body='Does it fit in a train luggage rack?', created_at=_ago(24 * 32)))
    session.add(
        Message(
            conversation_id=conv_brompton.id,
            author_handle='jana.b',
            body='Yes, folded it fits overhead — I commute with it daily.',
            created_at=_ago(24 * 32 - 1),
        )
    )

    kids = add(
        Listing(
            title='Kids bike 20" — training wheels included',
            description='Outgrown, some scratches. Perfect starter bike.',
            price_cents=4500,
            condition=Condition.fair,
            category='bikes',
            location='Kreuzberg · 2 km',
            image_url='https://images.unsplash.com/photo-1476990789491-712b869b91a5?w=800&h=600&fit=crop&q=75&auto=format',
            seller_handle='jana.b',
            created_at=_ago(24 * 64),
            sold_at=_ago(24 * 60),
        )
    )
    kids.status = 'sold'
    _event(session, kids, 'listed', 'Listed — kids bike 20"', None, 24 * 64)
    _event(session, kids, 'sold', 'Sold — conversations with buyers are now public', None, 24 * 60)

    conv_kids = Conversation(listing_id=kids.id, buyer_handle='marat_77', is_public=False, created_at=_ago(24 * 62))
    session.add(conv_kids)
    session.flush()
    session.add(
        Message(
            conversation_id=conv_kids.id, author_handle='marat_77', body='Is the seat height adjustable? Asking for a 6-year-old.', created_at=_ago(24 * 62)
        )
    )
    session.add(
        Message(
            conversation_id=conv_kids.id,
            author_handle='jana.b',
            body='Yes, plenty of room to grow. Training wheels come off in five minutes.',
            created_at=_ago(24 * 61),
        )
    )

    session.add(
        Rating(
            listing_id=brompton.id,
            rater_handle='tomsfamily',
            ratee_handle='jana.b',
            stars=5,
            text='Third purchase from jana. Fair prices, honest condition notes every time.',
            created_at=_ago(24 * 30 - 1),
        )
    )
    session.add(
        Rating(
            listing_id=kids.id, rater_handle='milan', ratee_handle='jana.b', stars=4, text='Fine sale, honest about the scratches.', created_at=_ago(24 * 59)
        )
    )
    session.add(
        Rating(listing_id=kids.id, rater_handle='jana.b', ratee_handle='milan', stars=5, text='Straightforward, met on time.', created_at=_ago(24 * 59 - 1))
    )

    # Ratings on the sold cube — two-sided.
    session.add(
        Rating(
            listing_id=cube.id,
            rater_handle='milan',
            ratee_handle='lea_rides',
            stars=5,
            text='Bike exactly as described, met at her place, let me bring a friend to check it. Zero hesitation.',
            created_at=_ago(24 * 6 - 2),
        )
    )
    session.add(
        Rating(
            listing_id=cube.id,
            rater_handle='lea_rides',
            ratee_handle='milan',
            stars=5,
            text='Straightforward buyer, on time, fair negotiation in the open.',
            created_at=_ago(24 * 6 - 3),
        )
    )
    session.add(
        Rating(
            listing_id=cube.id,
            rater_handle='tomsfamily',
            ratee_handle='lea_rides',
            stars=4,
            text='Fine sale. Slight delay at the meet but honest condition notes.',
            created_at=_ago(24 * 30),
        )
    )
