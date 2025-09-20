import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_ping(): 
    client = TestClient(app)
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["message"] == "pong"

def test_register_and_login(): 
    client = TestClient(app)
    data = {"username": "pytestuser", "email": "pytestuser@example.com", "password": "pytestpass123"}
    r = client.post("/register", json=data)
    assert r.status_code in (200, 400)  # 400 если уже есть
    r = client.post("/login", data={"username": "pytestuser", "password": "pytestpass123"})
    assert r.status_code == 200
    assert "access_token" in r.json()
