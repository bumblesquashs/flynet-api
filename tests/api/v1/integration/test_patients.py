from fastapi.testclient import TestClient
from model.patient import PatientModel

from helpers import test_data
from helpers.auth import authorize


def test_search_endpoint(client: TestClient):
    """
    Search endpoint with no params should return all 3 patients
    """
    token = authorize(client)
    response = client.get("/patient/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    search_results = response.json()
    assert search_results['total'] == 3

    patient_list = search_results['items']
    assert len(patient_list) == 3  # expect 2 patients

    first_patient = PatientModel(**patient_list[0])
    assert first_patient.id == 1
    assert first_patient.first_name == "Adans"
    assert first_patient.last_name == "Batista"
    assert first_patient.email == "adans@calicologic.com"

    second_patient = PatientModel(**patient_list[1])
    assert second_patient.id == 2
    assert second_patient.first_name == "James"
    assert second_patient.last_name == "Ward"
    assert second_patient.email == "james@calicologic.com"


def test_search_endpoint_limit_1(client: TestClient):
    """
    Search endpoint with limit 1 should return first patient
    """
    token = authorize(client)
    response = client.get("/patient", headers={"Authorization": f"Bearer {token}"}, params={"limit": "1"})

    assert response.status_code == 200
    search_results = response.json()
    assert search_results['total'] == 3

    patient_list = search_results['items']
    assert len(patient_list) == 1  # expect 1 patient

    first_patient = PatientModel(**patient_list[0])
    assert first_patient.id == 1  # expect 1st patient


def test_search_endpoint_offset_1(client: TestClient):
    """
    Search endpoint with offset 1 should return second of three patients
    """
    token = authorize(client)
    response = client.get("/patient", headers={"Authorization": f"Bearer {token}"}, params={"offset": "1"})

    assert response.status_code == 200
    search_results = response.json()
    assert search_results['total'] == 3

    patient_list = search_results['items']
    assert len(patient_list) == 2  # expect 1 patient

    first_patient = PatientModel(**patient_list[0])
    assert first_patient.id == 2  # expect 2nd patient


def test_get_by_id(client: TestClient):
    """
    Get by id endpoint test
    """
    token = authorize(client)
    response = client.get("/patient/1", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()

    patient = PatientModel(**body)
    assert patient.id == 1
    assert patient.first_name == "Adans"
    assert patient.last_name == "Batista"
    assert patient.email == "adans@calicologic.com"


def test_create_get_delete(client: TestClient):
    """
    Test creating a new patient, getting it, then deleting it
    """
    token = authorize(client)
    new_patient = test_data.test_patient_create

    # Create
    response = client.post("/patient/", headers={"Authorization": f"Bearer {token}"}, json=new_patient)
    assert response.status_code == 200
    body = response.json()
    assert body["lastName"] == "testlast"
    created_id = body["id"]

    # Get By id
    response = client.get(f"/patient/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    patient = PatientModel(**body)
    assert patient.id == created_id
    assert patient.first_name == "testfirst"
    assert patient.last_name == "testlast"

    # Delete by id
    response = client.delete(f"/patient/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    patient = PatientModel(**body)
    assert patient.id == created_id

    # Get should now fail
    response = client.get(f"/patient/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_create_update_delete(client: TestClient):
    """data
    Test creating a new patient, getting it, then deleting it
    """
    token = authorize(client)
    new_patient = test_data.test_patient_create

    # Create
    response = client.post("/patient/", headers={"Authorization": f"Bearer {token}"}, json=new_patient)
    assert response.status_code == 200
    body = response.json()
    assert body["lastName"] == "testlast"
    created_id = body["id"]

    # Update
    patient_to_update = test_data.test_patient_update
    response = client.put(f"/patient/{created_id}", headers={"Authorization": f"Bearer {token}"}, json=patient_to_update)

    assert response.status_code == 200
    body = response.json()
    patient = PatientModel(**body)
    assert patient.id == created_id
    assert patient.first_name == "NEWFIRSTNAME"
    assert patient.last_name == "NEWLASTNAME"

    # Delete by id
    response = client.delete(f"/patient/{created_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    patient = PatientModel(**body)
    assert patient.id == created_id


def test_get_by_id_failure(client: TestClient):
    """
    Get by id endpoint test, but with an invalid id, so bad request
    """
    token = authorize(client)
    response = client.get("/patient/69", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Patient not found."
