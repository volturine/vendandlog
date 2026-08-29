"""API contract tests — the soul invariants live here."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.db as db
from app.main import create_app
from app.seed import _seed


@pytest.fixture(name='client')
def client_fixture():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    db.engine = engine
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed(session)
        session.commit()
    app = create_app()
    app.router.on_startup = []
    return TestClient(app)


def test_health(client):
    assert client.get('/api/health').json() == {'status': 'ok'}


def test_browse_returns_active_by_default(client):
    listings = client.get('/api/listings').json()
    assert listings
    assert all(entry['status'] == 'active' for entry in listings)


def test_sold_stays_browsable(client):
    all_listings = client.get('/api/listings', params={'status': 'all'}).json()
    sold = [entry for entry in all_listings if entry['status'] == 'sold']
    assert sold, 'sold listings must remain in the public record'
    assert all(entry['public_conversation_count'] >= 1 for entry in sold)


def test_listing_log_is_chained(client):
    detail = client.get('/api/listings/1').json()
    events = detail['events']
    assert len(events) >= 2
    hashes = {e['hash'] for e in events}
    assert len(hashes) == len(events)


def test_private_conversation_hidden_from_strangers(client):
    detail = client.get('/api/listings/1').json()
    conversations = detail['conversations']
    # anonymous (no X-Acting-As) must not see the private conversation messages
    assert all(not c['is_public'] for c in conversations)
    conv_id = conversations[0]['id']
    response = client.get(f'/api/conversations/{conv_id}')
    assert response.status_code == 403


def test_participant_reads_own_private_conversation(client):
    detail = client.get('/api/listings/1', headers={'X-Acting-As': 'jana.b'}).json()
    conversations = detail['conversations']
    conv_id = conversations[0]['id']
    response = client.get(f'/api/conversations/{conv_id}', headers={'X-Acting-As': 'jana.b'})
    assert response.status_code == 200
    assert len(response.json()['messages']) >= 2


def test_sale_makes_conversations_public(client):
    # create + sell a fresh listing as jana.b with a buyer conversation
    created = client.post(
        '/api/listings',
        headers={'X-Acting-As': 'jana.b'},
        json={'title': 'Test bike', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    conv = client.post(
        f'/api/listings/{created["id"]}/conversations',
        headers={'X-Acting-As': 'milan'},
        json={'body': 'interested'},
    ).json()
    assert conv['is_public'] is False

    response = client.post(
        f'/api/listings/{created["id"]}/status',
        headers={'X-Acting-As': 'jana.b'},
        json={'action': 'sold'},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'sold'

    stranger_view = client.get(f'/api/conversations/{conv["id"]}')
    assert stranger_view.status_code == 200, 'sale must make the conversation public'


def test_sold_listing_is_read_only(client):
    created = client.post(
        '/api/listings',
        headers={'X-Acting-As': 'jana.b'},
        json={'title': 'Test bike 2', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    client.post(
        f'/api/listings/{created["id"]}/status',
        headers={'X-Acting-As': 'jana.b'},
        json={'action': 'sold'},
    )
    response = client.patch(
        f'/api/listings/{created["id"]}',
        headers={'X-Acting-As': 'jana.b'},
        json={'price': 50},
    )
    assert response.status_code == 409


def test_price_drop_appends_event(client):
    created = client.post(
        '/api/listings',
        headers={'X-Acting-As': 'jana.b'},
        json={'title': 'Test bike 3', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    client.patch(
        f'/api/listings/{created["id"]}',
        headers={'X-Acting-As': 'jana.b'},
        json={'price': 80},
    )
    events = client.get(f'/api/listings/{created["id"]}/events').json()
    assert events[0]['kind'] == 'price_drop'


def test_ratings_unlock_after_sale_and_are_once(client):
    created = client.post(
        '/api/listings',
        headers={'X-Acting-As': 'jana.b'},
        json={'title': 'Test bike 4', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    client.post(
        f'/api/listings/{created["id"]}/conversations',
        headers={'X-Acting-As': 'milan'},
        json={'body': 'hi'},
    )
    early = client.post(
        '/api/ratings',
        headers={'X-Acting-As': 'milan'},
        json={'listing_id': created['id'], 'stars': 5, 'text': ''},
    )
    assert early.status_code == 409

    client.post(
        f'/api/listings/{created["id"]}/status',
        headers={'X-Acting-As': 'jana.b'},
        json={'action': 'sold'},
    )
    first = client.post(
        '/api/ratings',
        headers={'X-Acting-As': 'milan'},
        json={'listing_id': created['id'], 'stars': 5, 'text': 'great'},
    )
    assert first.status_code == 200
    again = client.post(
        '/api/ratings',
        headers={'X-Acting-As': 'milan'},
        json={'listing_id': created['id'], 'stars': 1, 'text': ''},
    )
    assert again.status_code == 409


def test_unhide_makes_conversation_public_and_logs_it(client):
    created = client.post(
        '/api/listings',
        headers={'X-Acting-As': 'jana.b'},
        json={'title': 'Test bike 5', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    conv = client.post(
        f'/api/listings/{created["id"]}/conversations',
        headers={'X-Acting-As': 'milan'},
        json={'body': 'you there?'},
    ).json()
    response = client.post(
        f'/api/conversations/{conv["id"]}/unhide',
        headers={'X-Acting-As': 'milan'},
    )
    assert response.status_code == 200
    assert response.json()['is_public'] is True
    events = client.get(f'/api/listings/{created["id"]}/events').json()
    assert events[0]['kind'] == 'conversation_public'


def test_flags_raise_trust_stakes(client):
    before = client.get('/api/users/marat_77').json()
    response = client.post(
        '/api/flags',
        headers={'X-Acting-As': 'jana.b'},
        json={'handle': 'marat_77', 'reason': 'no-show x2, chat unhidden as proof'},
    )
    assert response.status_code == 200
    after = client.get('/api/users/marat_77').json()
    assert after['flags_upheld'] == before['flags_upheld'] + 1
    assert after['trust_score'] < before['trust_score']


def test_trust_score_present_and_sane(client):
    user = client.get('/api/users/lea_rides').json()
    assert user['trust_score'] > 0
    assert 0 <= user['positive_pct'] <= 100
