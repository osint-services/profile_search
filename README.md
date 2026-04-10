# profile_search

`profile_search` is an OSINT microservice that searches the profile of a given URL and returns metadata found at that site using [Tweepy](https://docs.tweepy.org/en/stable/).

## Requirements
- Python 3.9 or higher

### Tech Stack
- [FastAPI](https://fastapi.tiangolo.com/)
- [Tweepy](https://docs.tweepy.org/en/stable/)
- [python-dotenv](https://saurabh-kumar.com/python-dotenv/)

### Setup
1. Create a Python virtual environment: `python -m venv .venv`
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy the environment file template: `cp .env.example .env`
5. Add your Twitter bearer token to `.env` using the `TWEEPY_BEARER_TOKEN` variable.

### Run the app
From the repository root, start the FastAPI server:

```bash
uvicorn profile_search.server:app --reload
```

### API Usage
Send a GET request to the `/focus` endpoint with a `url` query parameter.

Example:

```bash
curl "http://127.0.0.1:8000/focus?url=https://twitter.com/Twitter"
```

The service returns JSON metadata for the profile found at the provided URL.