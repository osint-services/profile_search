import os
from pathlib import Path

import tweepy
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import Any

# Load environment variables from .env file
load_dotenv(Path(__file__).parent / ".env")

def x_username_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    return path.split("/")[0]


def search_profile(arg_url: str) -> dict:
    bearer_token = os.getenv("TWEEPY_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")
    if not bearer_token:
        raise RuntimeError(
            "Missing TWEEPY_BEARER_TOKEN environment variable. "
            "Set TWEEPY_BEARER_TOKEN before running the app."
        )

    username = x_username_from_url(arg_url)

    client = tweepy.Client(bearer_token=bearer_token)

    resp: Any = client.get_user(
        username=username,
        user_fields=[
            "created_at",
            "description",
            "location",
            "profile_image_url",
            "protected",
            "public_metrics",
            "url",
            "verified",
        ],
    )

    user = resp.data
    if not user:
        return {}

    return {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "bio": user.description,
        "location": getattr(user, "location", None),
        "profile_image_url": getattr(user, "profile_image_url", None),
        "website": getattr(user, "url", None),
        "verified": getattr(user, "verified", None),
        "protected": getattr(user, "protected", None),
        "created_at": str(getattr(user, "created_at", None)),
        "metrics": getattr(user, "public_metrics", None),
    }