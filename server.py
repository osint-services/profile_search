from fastapi import FastAPI
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

@app.get('/focus')
def find_profile(url: str):
    profile_info = search_profile(url)
    return profile_info