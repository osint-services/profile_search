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
            "entities",
            "location",
            "most_recent_tweet_id",
            "pinned_tweet_id",
            "profile_banner_url",
            "profile_image_url",
            "protected",
            "public_metrics",
            "url",
            "verified",
            "verified_type",
            "withheld",
        ],
    )

    user = resp.data
    if not user:
        return {}

    return {
        "id": str(user.id),
        "name": user.name,
        "username": user.username,
        "bio": user.description,
        "location": getattr(user, "location", None),
        "entities": getattr(user, "entities", None),
        "most_recent_tweet_id": getattr(user, "most_recent_tweet_id", None),
        "pinned_tweet_id": getattr(user, "pinned_tweet_id", None),
        "profile_banner_url": getattr(user, "profile_banner_url", None),
        "profile_image_url": getattr(user, "profile_image_url", None),
        "website": getattr(user, "url", None),
        "verified": getattr(user, "verified", None),
        "verified_type": getattr(user, "verified_type", None),
        "protected": getattr(user, "protected", None),
        "withheld": getattr(user, "withheld", None),
        "created_at": (
            str(user.created_at)
            if getattr(user, "created_at", None) is not None
            else None
        ),
        "metrics": getattr(user, "public_metrics", None),
    }
