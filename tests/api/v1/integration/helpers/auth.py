from fastapi.testclient import TestClient


def authorize(client: TestClient):
    response = client.post("/token", data={"username": "admin@calicologic.com", "password": "Testing11*"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token
