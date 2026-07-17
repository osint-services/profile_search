import os

import tweepy
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .profile_search import search_profile

app = FastAPI()

origins = [
    "http://localhost:3000"
]


def describe_x_api_error(exc: Exception) -> tuple[int, str]:
    provider_status = getattr(getattr(exc, "response", None), "status_code", None)
    api_messages = getattr(exc, "api_messages", None) or []
    provider_message = " ".join(str(message) for message in api_messages).strip()
    if not provider_message:
        provider_message = str(exc).strip()

    if provider_status == 402 or "credits depleted" in provider_message.lower():
        return (
            status.HTTP_402_PAYMENT_REQUIRED,
            "X API credits are depleted. Add credits or update the X developer project before inspecting profiles.",
        )
    if provider_status == 429:
        return (
            status.HTTP_429_TOO_MANY_REQUESTS,
            "The X API rate limit has been reached. Wait for the limit to reset and try again.",
        )
    if provider_status in {401, 403}:
        return (
            status.HTTP_502_BAD_GATEWAY,
            "X rejected the configured bearer token or its project access. Check the X integration credentials and access level.",
        )
    if provider_status == 404:
        return (
            status.HTTP_404_NOT_FOUND,
            "X could not find that public profile.",
        )
    return (
        status.HTTP_502_BAD_GATEWAY,
        "X profile lookup failed. Check the provider status and try again.",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/healthz')
def healthz():
    return {"status": "ok"}


@app.get('/readyz')
def readyz():
    if not (os.getenv("TWEEPY_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Profile inspection is not configured: TWEEPY_BEARER_TOKEN is missing.",
        )
    return {"status": "ready"}


@app.get('/focus')
def find_profile(url: str):
    try:
        return search_profile(url)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except tweepy.TweepyException as exc:
        response_status, detail = describe_x_api_error(exc)
        raise HTTPException(status_code=response_status, detail=detail) from exc
