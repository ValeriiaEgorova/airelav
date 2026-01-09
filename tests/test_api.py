from unittest.mock import patch

from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    response = client.post(
        "/auth/register", params={"email": "test@example.com", "password": "pass"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}


def test_login_user(client: TestClient):
    client.post("/auth/register", params={"email": "user@test.com", "password": "123"})

    response = client.post(
        "/token", data={"username": "user@test.com", "password": "123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]


def test_create_generation_task(client: TestClient):
    token = test_login_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("main.run_generation_wrapper"):
        response = client.post(
            "/generate",
            json={"prompt": "Test dataset", "model": "gemini-1.5-flash"},
            headers=headers,
        )

        if response.status_code != 200:
            print(response.json())

        assert response.status_code == 200
        assert "task_id" in response.json()


def test_history_protected(client: TestClient):
    response = client.get("/conversations")
    assert response.status_code == 401
