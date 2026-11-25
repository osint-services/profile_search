import sys
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from profile_search.server import app


def mock_provider(monkeypatch, handler):
    monkeypatch.setenv("TWEEPY_BEARER_TOKEN", "fixture-token")
    transport = httpx.MockTransport(handler)
    client_class = httpx.Client

    def request(url, **kwargs):
        with client_class(transport=transport, timeout=kwargs.pop("timeout")) as client:
            return client.get(url, **kwargs)

    monkeypatch.setattr(httpx, "get", request)


def test_profile_contract_uses_existing_bearer_token(monkeypatch):
    def provider(request):
        assert request.url.host == "api.x.com"
        assert request.url.path == "/2/users/by/username/example"
        assert request.headers["Authorization"] == "Bearer fixture-token"
        assert {"description", "created_at", "public_metrics"} <= set(
            request.url.params["user.fields"].split(",")
        )
        return httpx.Response(200, json={"data": {
            "id": "123",
            "name": "Example",
            "username": "example",
            "description": "Fixture profile",
            "created_at": "2026-01-01T00:00:00Z",
            "public_metrics": {"followers_count": 1},
        }})

    mock_provider(monkeypatch, provider)
    with TestClient(app) as client:
        response = client.get("/focus", params={"url": "https://x.com/example"})
    assert response.status_code == 200
    profile = response.json()
    assert profile["id"] == "123"
    assert profile["bio"] == "Fixture profile"
    assert profile["created_at"] == "2026-01-01 00:00:00+00:00"
    assert profile["metrics"] == {"followers_count": 1}
    assert profile["location"] is None


@pytest.mark.parametrize("provider_status,message,expected,summary", [
    (402, "billing", 402, "credits are depleted"),
    (403, "credits depleted", 402, "credits are depleted"),
    (429, "Too Many Requests", 429, "rate limit"),
    (401, "raw upstream credential failure", 502, "bearer token"),
    (404, "not found", 404, "could not find"),
])
def test_provider_errors_are_actionable(monkeypatch, provider_status, message, expected, summary):
    mock_provider(monkeypatch, lambda request: httpx.Response(provider_status, json={"detail": message}))
    with TestClient(app) as client:
        response = client.get("/focus", params={"url": "https://x.com/example"})
    assert response.status_code == expected
    assert summary in response.json()["detail"]
    assert "raw upstream" not in response.json()["detail"]


def test_provider_timeout_returns_bad_gateway(monkeypatch):
    def provider(request):
        raise httpx.ReadTimeout("raw upstream timing detail", request=request)

    mock_provider(monkeypatch, provider)
    with TestClient(app) as client:
        response = client.get("/focus", params={"url": "https://x.com/example"})
    assert response.status_code == 502
    assert "raw upstream" not in response.json()["detail"]


def test_invalid_username_is_rejected_before_provider_call(monkeypatch):
    monkeypatch.setenv("TWEEPY_BEARER_TOKEN", "fixture-token")

    def unexpected_call(*args, **kwargs):
        pytest.fail("invalid username reached the provider")

    monkeypatch.setattr(httpx, "get", unexpected_call)
    with TestClient(app) as client:
        response = client.get("/focus", params={"url": "https://x.com/"})
    assert response.status_code == 400
