import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .profile_search import search_profile

app = FastAPI()

origins = [
    "http://localhost:3000"
]

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
