import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_ping():
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["message"] == "pong"

def test_create_order():
    client = TestClient(app)
    data = {"user_id": 1, "products": [{"product_id": 1, "quantity": 1}]}
    r = client.post("/orders", json=data)
    assert r.status_code in (201, 404)
    r = client.get("/orders")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
