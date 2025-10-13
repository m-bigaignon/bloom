from collections import abc

import pytest
from fastapi.testclient import TestClient

from tests.example.entrypoints.api import app


@pytest.fixture
def client() -> abc.Generator[TestClient]:
    with TestClient(app) as client:
        yield client
