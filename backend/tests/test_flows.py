from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from backend.app import database
from backend.app.database import get_session
from backend.app.main import create_app
from backend.app.seed import seed


def build_client() -> TestClient:
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    database.engine = test_engine
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        seed(session)

    app = create_app()

    def get_session_override():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    return TestClient(app)


def test_event_response_flow():
    client = build_client()
    headers = {"X-User-Id": "3"}  # player

    response = client.post("/events/1/respond", params={"response": "accepted"}, headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["response"] == "accepted"

    responses = client.get("/events/1/responses").json()
    assert len(responses) == 1
    assert responses[0]["user_id"] == 3


def test_assign_fine_updates_balance_and_ledger():
    client = build_client()
    headers = {"X-User-Id": "2"}  # treasurer

    assignment = {
        "fine_id": 1,
        "user_id": 3,
        "event_id": 1,
    }
    resp = client.post("/fines/assign", json=assignment, headers=headers)
    assert resp.status_code == 201

    balance = client.get("/ledger/3/balance").json()
    assert balance["balance_cents"] == -500

    entries = client.get("/ledger").json()
    assert any(entry["category"] == "fine" for entry in entries)


def test_drink_booking_reduces_stock():
    client = build_client()
    headers = {"X-User-Id": "3"}

    before = client.get("/drinks").json()[0]
    resp = client.post("/drinks/1/book", params={"quantity": 2}, headers=headers)
    assert resp.status_code == 201

    after = client.get("/drinks").json()[0]
    assert after["stock"] == before["stock"] - 2
