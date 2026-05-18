import requests
import pytest

BASE_URL = "http://localhost:8080/api"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_invalid():
    response = requests.post(f"{BASE_URL}/login", data={"username": "wrong", "password": "wrong"})
    assert response.status_code == 401

# Note: Requires seeded admin or created user to fully test auth endpoints
