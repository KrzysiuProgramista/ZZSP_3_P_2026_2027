import pytest
from fastapi.testclient import TestClient

from app.main import app, get_service
from app.service import BookmarkService


@pytest.fixture
def service() -> BookmarkService:
    """A fresh store per test so tests cannot leak into each other."""
    return BookmarkService()


@pytest.fixture
def client(service: BookmarkService) -> TestClient:
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
