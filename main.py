from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

app = FastAPI()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")


@app.get("/")
def home():
    return {"status": "TikTok automation server running"}


@app.get("/auth/tiktok")
def tiktok_login():

    state = secrets.token_urlsafe(32)

    authorization_url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        "&response_type=code"
        "&scope=user.info.basic"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )

    return RedirectResponse(authorization_url)