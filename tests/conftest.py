from collections import abc

import pytest
from fastapi.testclient import TestClient

from tests.app.entrypoints.api import app


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio backend for tests."""
    return "asyncio"


@pytest.fixture
def client() -> abc.Generator[TestClient]:
    with TestClient(app) as client:
        yield client
