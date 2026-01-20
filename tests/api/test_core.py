from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """
    Status endpoint should return OK.
    """
    response = client.get("/status")

    assert response.status_code == 200
    assert response.json() == {"status": "Healthy"}
