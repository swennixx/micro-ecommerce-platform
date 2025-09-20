import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_ping():
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["message"] == "pong"

def test_create_payment():
    client = TestClient(app)
    data = {"order_id": 1, "amount": 10.0}
    r = client.post("/payments", json=data)
    assert r.status_code in (201, 404)
    r = client.get("/payments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
