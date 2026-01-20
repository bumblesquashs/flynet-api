from fastapi.testclient import TestClient
from model.user import UserModel

from helpers import test_data
from helpers.auth import authorize


def test_search_endpoint(client: TestClient):
    """
    Search endpoint with no params should return all users
    """
    token = authorize(client)
    response = client.get("/user/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    user_list = response.json()

    assert len(user_list["items"]) == 2  # expect 2 users

    first_user = UserModel(**user_list["items"][0])
    assert first_user.id == 1
    assert first_user.first_name == "Admin"
    assert first_user.last_name == "User"
    assert first_user.email == "admin@calicologic.com"

    second_user = UserModel(**user_list["items"][1])
    assert second_user.id == 2
    assert second_user.first_name == "Staff"
    assert second_user.last_name == "User"
    assert second_user.email == "staff@calicologic.com"


def test_get_by_id(client: TestClient):
    """
    Get by id endpoint test
    """
    token = authorize(client)
    response = client.get("/user/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()

    user = UserModel(**body)
    assert user.id == 1
    assert user.first_name == "Admin"
    assert user.last_name == "User"
    assert user.email == "admin@calicologic.com"


def test_create_update_delete(client: TestClient):
    """
    Test creating a new user, updating it, then deleting it
    """
    token = authorize(client)
    new_user = test_data.test_user_create

    # Create
    response = client.post("/user/", headers={"Authorization": f"Bearer {token}"}, json=new_user)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "test@calicologic.com"
    assert body["firstName"] == "TestFirst"
    assert body["lastName"] == "TestLast"
    created_id = body["id"]

    # Update By id
    update_user = test_data.test_user_update
    response = client.put(f"/user/{created_id}", headers={"Authorization": f"Bearer {token}"}, json=update_user)

    assert response.status_code == 200
    body = response.json()
    user = UserModel(**body)
    assert user.id == created_id
    assert user.first_name == "ChangedFirst"
    assert user.last_name == "ChangedLast"
    assert user.role_id == 1

    # Delete by id
    response = client.delete(f"/user/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    patient = UserModel(**body)
    assert patient.id == created_id

    # Get should now fail
    response = client.get(f"/user/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
