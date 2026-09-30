import os
os.environ["DATABASE_URL"] = "sqlite:///./test_pocketsmart.db"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def unique_email():
    import uuid
    return f"test-{uuid.uuid4().hex[:10]}@example.com"


def test_register_login_session_and_home():
    email = unique_email()
    r = client.post("/api/register", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r = client.post("/api/login", json={"email": email, "password": "password123"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    token = r.json()["token"]
    client.cookies.set("access_token", token)

    r = client.get("/api/session-info")
    assert r.status_code == 200
    assert r.json()["email"] == email

    payload = {
        "budget": 25000,
        "rooms": ["Living Room", "Bedroom"],
        "items": [
            {"category": "lights", "quantity": 2},
            {"category": "ceiling fan", "quantity": 1},
        ],
        "style": "modern",
        "city": "Chennai",
    }
    r = client.post("/api/generate-home", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["budget"] == 25000
    assert body["recommendations"]


def test_party_and_history():
    email = unique_email()
    client.post("/api/register", json={"email": email, "password": "password123"})
    login = client.post("/api/login", json={"email": email, "password": "password123"})
    client.cookies.set("access_token", login.json()["token"])

    r = client.post("/api/generate-party", json={
        "budget": 20000, "guests": 40, "event_type": "birthday",
        "venue": "home", "city": "Chennai", "preferences": "simple"
    })
    assert r.status_code == 200
    assert r.json()["allocations"]

    r = client.post("/api/generate-jewelry", data={
        "budget": "5000", "occasion": "wedding", "style": "traditional",
        "outfit_color": "blue", "preferences": "lightweight"
    })
    assert r.status_code == 200
    assert r.json()["recommendations"]

    r = client.get("/api/history")
    assert r.status_code == 200
    assert len(r.json()["items"]) >= 2
