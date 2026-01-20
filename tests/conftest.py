import pytest
from sqlalchemy.orm import Session

from portal import app
from starlette.testclient import TestClient
from utils import get_client
from utils.populate import all_data


@pytest.fixture(scope="module")
def client() -> TestClient:
    # Drop test db data before every module runs... avoids db changes from some modules affecting other ones
    # FYI each test file is a module. Tests within a module can still affect other tests in that module, though.
    all_data(drop_db=True)
    return get_client(app)


@pytest.fixture(scope="module")
def database() -> Session:
    return all_data(drop_db=True)
