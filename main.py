import os
import secrets
import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")

# Temporaire : stockage du state en mémoire
oauth_states = set()


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "TikTok automation API is running"
    }


@app.get("/auth/tiktok")
def tiktok_login():

    state = secrets.token_urlsafe(32)
    oauth_states.add(state)

    url = (
        "https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={TIKTOK_CLIENT_KEY}"
        "&response_type=code"
        "&scope=user.info.basic"
        f"&redirect_uri={TIKTOK_REDIRECT_URI}"
        f"&state={state}"
    )

    return RedirectResponse(url)


@app.get("/auth/tiktok/callback")
def tiktok_callback(code: str = None, state: str = None):

    # Vérification du state
    if not state or state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state"
        )

    # Le state ne doit être utilisé qu'une seule fois
    oauth_states.remove(state)

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code"
        )

    # Échange du code contre un access token
    response = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": TIKTOK_REDIRECT_URI,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to get access token",
                "tiktok_response": response.text,
            },
        )

    token_data = response.json()

    # Pour le moment on affiche seulement les informations
    # nécessaires au développement.
    return {
        "success": True,
        "token_data": token_data,
    }