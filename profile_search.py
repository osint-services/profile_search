import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

USER_FIELDS = ",".join((
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
))


class InvalidProfileURL(ValueError):
    pass


class InvalidXResponse(Exception):
    pass


def x_username_from_url(url: str) -> str:
    try:
        username = urlparse(url).path.strip("/").split("/")[0]
    except ValueError as exc:
        raise InvalidProfileURL("Provide a URL with a valid X username.") from exc
    if not re.fullmatch(r"[A-Za-z0-9_]{1,15}", username):
        raise InvalidProfileURL("Provide a URL with a valid X username.")
    return username


def search_profile(arg_url: str) -> dict:
    bearer_token = os.getenv("TWEEPY_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")
    if not bearer_token:
        raise RuntimeError(
            "Missing TWEEPY_BEARER_TOKEN environment variable. "
            "Set TWEEPY_BEARER_TOKEN before running the app."
        )

    username = x_username_from_url(arg_url)
    response = httpx.get(
        f"https://api.x.com/2/users/by/username/{username}",
        headers={"Authorization": f"Bearer {bearer_token}"},
        params={"user.fields": USER_FIELDS},
        timeout=15,
    )
    response.raise_for_status()
    try:
        payload = response.json()
        user = payload.get("data")
        if user is None:
            return {}
        created_at = user.get("created_at")
        if created_at is not None:
            created_at = str(datetime.fromisoformat(created_at.replace("Z", "+00:00")))
        return {
            "id": str(user["id"]),
            "name": user["name"],
            "username": user["username"],
            "bio": user.get("description"),
            "location": user.get("location"),
            "entities": user.get("entities"),
            "most_recent_tweet_id": user.get("most_recent_tweet_id"),
            "pinned_tweet_id": user.get("pinned_tweet_id"),
            "profile_banner_url": user.get("profile_banner_url"),
            "profile_image_url": user.get("profile_image_url"),
            "website": user.get("url"),
            "verified": user.get("verified"),
            "verified_type": user.get("verified_type"),
            "protected": user.get("protected"),
            "withheld": user.get("withheld"),
            "created_at": created_at,
            "metrics": user.get("public_metrics"),
        }
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise InvalidXResponse("X returned invalid profile data.") from exc
