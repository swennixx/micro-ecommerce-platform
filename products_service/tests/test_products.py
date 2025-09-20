import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_ping():
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["message"] == "pong"

def test_create_product():
    client = TestClient(app)
    data = {"name": "pytest product", "description": "pytest", "price": 1.23, "stock": 5}
    r = client.post("/products", json=data)
    assert r.status_code in (201, 400)
    r = client.get("/products")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
