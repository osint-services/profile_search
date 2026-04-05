# focus

focus is an OSINT microservice that searches the profile of a given URL and returns metadata found at that site using [Tweepy](https://docs.tweepy.org/en/stable/) to gather the data.

## Requirements
- Python 3.9 or higher

### Tech Stack
- The REST API framework being used is [FastAPI](https://fastapi.tiangolo.com/)
- The tool being used to query social media URLs is [Tweepy](https://docs.tweepy.org/en/stable/)


### Setup
1. Create Python virtual environment. `python -m venv venv`
2. Activate virtual environment. `source venv/bin/activate`
3. Install dependencies. `pip install -r requirements.txt`
4. Copy the environment file template. `cp .env.example .env`
5. Add your Twitter bearer token to `.env`. Get one from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
6. Start server. `fastapi dev profile_search.py`
