import requests
import pytest

BASE_URL = "http://localhost:8080/api"
AUTH_HEADERS = {}

def test_login_success():
    response = requests.post(f"{BASE_URL}/login", data={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    AUTH_HEADERS["Authorization"] = f"Bearer {token}"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

def test_get_my_groups():
    response = requests.get(f"{BASE_URL}/my-groups", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_list():
    response = requests.post(f"{BASE_URL}/lists?group_id=1&name=TestList", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["name"] == "TestList"

def test_get_active_lists():
    response = requests.get(f"{BASE_URL}/lists/active?group_id=1", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item():
    response = requests.post(f"{BASE_URL}/items?list_id=1&description=Milk&cost=2.50", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert response.json()["description"] == "Milk"

def test_get_items():
    response = requests.get(f"{BASE_URL}/items?list_id=1", headers=AUTH_HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
