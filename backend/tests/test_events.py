import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.deps import get_project_id, get_repository
from app.repository import InMemoryRepository
from app.routes import router


@pytest.fixture
def repo() -> InMemoryRepository:
    # api_key "proj_test" maps to a known project_id
    return InMemoryRepository(keys={"proj_test": "11111111-1111-1111-1111-111111111111"})


@pytest.fixture
def client(repo: InMemoryRepository) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_repository] = lambda: repo
    return TestClient(app)


def _payload(**overrides) -> dict:
    base = {
        "timestamp": "2026-06-17T14:32:00Z",
        "model": "claude-sonnet-4-6",
        "tokens_in": 1240,
        "tokens_out": 380,
        "cost_usd": 0.0058,
        "duration_ms": 1240,
        "success": True,
        "tags": {"team": "backend", "feature": "search", "env": "prod"},
    }
    base.update(overrides)
    return base


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_post_event_accepted(client: TestClient, repo: InMemoryRepository):
    r = client.post(
        "/v1/events",
        json=_payload(),
        headers={"Authorization": "Bearer proj_test"},
    )
    assert r.status_code == 202
    assert "id" in r.json()

    assert len(repo.events) == 1
    project_id, event = repo.events[0]
    assert project_id == "11111111-1111-1111-1111-111111111111"
    assert event.model == "claude-sonnet-4-6"
    assert event.tags.feature == "search"


def test_missing_auth_rejected(client: TestClient):
    r = client.post("/v1/events", json=_payload())
    assert r.status_code == 401


def test_invalid_api_key_rejected(client: TestClient):
    r = client.post(
        "/v1/events",
        json=_payload(),
        headers={"Authorization": "Bearer proj_wrong"},
    )
    assert r.status_code == 401


def test_malformed_auth_header_rejected(client: TestClient):
    r = client.post(
        "/v1/events",
        json=_payload(),
        headers={"Authorization": "proj_test"},  # missing "Bearer "
    )
    assert r.status_code == 401


def test_negative_tokens_rejected(client: TestClient):
    r = client.post(
        "/v1/events",
        json=_payload(tokens_in=-5),
        headers={"Authorization": "Bearer proj_test"},
    )
    assert r.status_code == 422


def test_optional_tags_and_duration(client: TestClient, repo: InMemoryRepository):
    payload = _payload(duration_ms=None, tags={"team": "ml"})
    r = client.post(
        "/v1/events", json=payload, headers={"Authorization": "Bearer proj_test"}
    )
    assert r.status_code == 202
    _, event = repo.events[0]
    assert event.duration_ms is None
    assert event.tags.team == "ml"
    assert event.tags.feature is None
