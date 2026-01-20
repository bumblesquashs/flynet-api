import logging

from core.dependencies import get_db
from fastapi import FastAPI
from fastapi.testclient import TestClient
from utils.database import get_test_db


def get_client(test_app: FastAPI) -> TestClient:
    test_app.dependency_overrides[get_db] = get_test_db
    return TestClient(test_app)


def get_log(name: str, logging_level: str) -> logging.Logger:
    """
    Configure a basic logger, and return it, if we need to output any information about the application
    configuration, this function will give a functional logger.
    :return: a configured logger instance.
    """
    internal_logger = logging.getLogger(name=name)
    internal_handler = logging.StreamHandler()
    internal_handler.setFormatter(logging.Formatter("%(levelname)s  [%(name)s] %(message)s"))
    internal_logger.addHandler(internal_handler)
    internal_logger.setLevel(logging_level)
    return internal_logger
