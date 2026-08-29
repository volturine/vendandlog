"""API contract tests — the soul invariants live here."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.db as db
from app.main import create_app
from app.seed import _seed


@pytest.fixture(name='app')
def app_fixture():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    db.engine = engine
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed(session)
        session.commit()
    return create_app()


def client_as(app, handle: str | None = None) -> TestClient:
    """A fresh browser: signed in as handle via the real login flow, or anonymous."""
    client = TestClient(app)
    if handle:
        response = client.post('/api/auth/login', json={'handle': handle, 'password': 'demo'})
        assert response.status_code == 200, response.text
    return client


def test_health(app):
    assert client_as(app).get('/api/health').json() == {'status': 'ok'}


def test_register_login_logout(app):
    client = client_as(app)
    registered = client.post(
        '/api/auth/register',
        json={'handle': 'newbie', 'name': 'New Buyer', 'password': 'secret1'},
    )
    assert registered.status_code == 200
    assert registered.json()['handle'] == 'newbie'
    assert client.get('/api/me').json()['handle'] == 'newbie'

    assert client.post('/api/auth/logout').status_code == 200
    assert client.get('/api/me').json() is None

    again = client.post('/api/auth/login', json={'handle': 'newbie', 'password': 'secret1'})
    assert again.status_code == 200
    assert client.get('/api/me').json()['handle'] == 'newbie'


def test_login_rejects_wrong_password(app):
    client = client_as(app)
    response = client.post('/api/auth/login', json={'handle': 'jana.b', 'password': 'wrong'})
    assert response.status_code == 401


def test_register_rejects_duplicate_and_bad_handle(app):
    client = client_as(app)
    assert client.post('/api/auth/register', json={'handle': 'jana.b', 'name': 'X', 'password': 'abcd'}).status_code == 409
    assert client.post('/api/auth/register', json={'handle': 'Bad Handle!', 'name': 'X', 'password': 'abcd'}).status_code == 422


def test_actions_require_sign_in(app):
    assert client_as(app).post('/api/listings', json={'title': 'x bike', 'description': 'x', 'price': 1}).status_code == 401


def test_browse_returns_active_by_default(app):
    listings = client_as(app).get('/api/listings').json()
    assert listings
    assert all(entry['status'] == 'active' for entry in listings)


def test_sold_stays_browsable(app):
    all_listings = client_as(app).get('/api/listings', params={'status': 'all'}).json()
    sold = [entry for entry in all_listings if entry['status'] == 'sold']
    assert sold, 'sold listings must remain in the public record'
    assert all(entry['public_conversation_count'] >= 1 for entry in sold)


def test_listing_log_is_chained(app):
    detail = client_as(app).get('/api/listings/1').json()
    events = detail['events']
    assert len(events) >= 2
    hashes = {e['hash'] for e in events}
    assert len(hashes) == len(events)


def test_private_conversation_hidden_from_strangers(app):
    detail = client_as(app).get('/api/listings/1').json()
    # strangers are not offered private conversations at all
    assert detail['conversations'] == []

    # and fetching one directly is forbidden
    jana = client_as(app, 'jana.b')
    conv_id = jana.get('/api/listings/1').json()['conversations'][0]['id']
    response = client_as(app).get(f'/api/conversations/{conv_id}')
    assert response.status_code == 403


def test_participant_reads_own_private_conversation(app):
    jana = client_as(app, 'jana.b')
    detail = jana.get('/api/listings/1').json()
    conv_id = detail['conversations'][0]['id']
    response = jana.get(f'/api/conversations/{conv_id}')
    assert response.status_code == 200
    assert len(response.json()['messages']) >= 2


def test_sale_makes_conversations_public(app):
    milan = client_as(app, 'milan')
    jana = client_as(app, 'jana.b')

    created = milan.post(
        '/api/listings',
        json={'title': 'Test bike', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    conv = jana.post(
        f'/api/listings/{created["id"]}/conversations',
        json={'body': 'interested'},
    ).json()
    assert conv['is_public'] is False

    response = milan.post(f'/api/listings/{created["id"]}/status', json={'action': 'sold'})
    assert response.status_code == 200
    assert response.json()['status'] == 'sold'

    stranger_view = client_as(app).get(f'/api/conversations/{conv["id"]}')
    assert stranger_view.status_code == 200, 'sale must make the conversation public'


def test_sold_listing_is_read_only(app):
    milan = client_as(app, 'milan')
    created = milan.post(
        '/api/listings',
        json={'title': 'Test bike 2', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    milan.post(f'/api/listings/{created["id"]}/status', json={'action': 'sold'})

    response = milan.patch(f'/api/listings/{created["id"]}', json={'price': 50})
    assert response.status_code == 409


def test_only_seller_can_sell(app):
    jana = client_as(app, 'jana.b')
    other = client_as(app, 'milan')
    created = jana.post(
        '/api/listings',
        json={'title': 'Test bike 6', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    response = other.post(f'/api/listings/{created["id"]}/status', json={'action': 'sold'})
    assert response.status_code == 403


def test_price_drop_appends_event(app):
    milan = client_as(app, 'milan')
    created = milan.post(
        '/api/listings',
        json={'title': 'Test bike 3', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    milan.patch(f'/api/listings/{created["id"]}', json={'price': 80})
    events = client_as(app).get(f'/api/listings/{created["id"]}/events').json()
    assert events[0]['kind'] == 'price_drop'


def test_ratings_unlock_after_sale_and_are_once(app):
    milan = client_as(app, 'milan')
    jana = client_as(app, 'jana.b')

    created = milan.post(
        '/api/listings',
        json={'title': 'Test bike 4', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    jana.post(f'/api/listings/{created["id"]}/conversations', json={'body': 'hi'})

    early = jana.post('/api/ratings', json={'listing_id': created['id'], 'stars': 5, 'text': ''})
    assert early.status_code == 409

    milan.post(f'/api/listings/{created["id"]}/status', json={'action': 'sold'})

    first = jana.post('/api/ratings', json={'listing_id': created['id'], 'stars': 5, 'text': 'great'})
    assert first.status_code == 200
    again = jana.post('/api/ratings', json={'listing_id': created['id'], 'stars': 1, 'text': ''})
    assert again.status_code == 409


def test_unhide_makes_conversation_public_and_logs_it(app):
    milan = client_as(app, 'milan')
    jana = client_as(app, 'jana.b')

    created = milan.post(
        '/api/listings',
        json={'title': 'Test bike 5', 'description': 'x', 'price': 100, 'category': 'bikes'},
    ).json()
    conv = jana.post(
        f'/api/listings/{created["id"]}/conversations',
        json={'body': 'you there?'},
    ).json()

    response = jana.post(f'/api/conversations/{conv["id"]}/unhide')
    assert response.status_code == 200
    assert response.json()['is_public'] is True

    events = client_as(app).get(f'/api/listings/{created["id"]}/events').json()
    assert events[0]['kind'] == 'conversation_public'


def test_flags_raise_trust_stakes(app):
    jana = client_as(app, 'jana.b')
    anonymous = client_as(app)

    before = anonymous.get('/api/users/marat_77').json()
    response = jana.post(
        '/api/flags',
        json={'handle': 'marat_77', 'reason': 'no-show x2, chat unhidden as proof'},
    )
    assert response.status_code == 200

    after = anonymous.get('/api/users/marat_77').json()
    assert after['flags_upheld'] == before['flags_upheld'] + 1
    assert after['trust_score'] < before['trust_score']


def test_trust_score_present_and_sane(app):
    user = client_as(app).get('/api/users/lea_rides').json()
    assert user['trust_score'] > 0
    assert 0 <= user['positive_pct'] <= 100
