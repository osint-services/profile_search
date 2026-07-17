import sys
from types import SimpleNamespace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from profile_search.server import describe_x_api_error


def provider_error(status_code, message):
    return SimpleNamespace(
        response=SimpleNamespace(status_code=status_code),
        api_messages=[message],
    )


def test_depleted_credits_are_actionable():
    status_code, message = describe_x_api_error(
        provider_error(402, "credits depleted")
    )

    assert status_code == 402
    assert "credits are depleted" in message


def test_rate_limits_are_preserved():
    status_code, message = describe_x_api_error(
        provider_error(429, "Too Many Requests")
    )

    assert status_code == 429
    assert "rate limit" in message


def test_invalid_provider_credentials_do_not_leak_details():
    status_code, message = describe_x_api_error(
        provider_error(401, "raw upstream credential failure")
    )

    assert status_code == 502
    assert "bearer token" in message
    assert "raw upstream" not in message
