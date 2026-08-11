import os
import secrets

import requests

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from dotenv import load_dotenv

from app.database import Base, SessionLocal, engine
from app.model import TikTokAccount


load_dotenv()

app = FastAPI()

TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
TIKTOK_REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")

oauth_states = set()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "TikTok automation API is running",
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
def tiktok_callback(
    code: str | None = None,
    state: str | None = None,
):

    if not state or state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    oauth_states.remove(state)

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code",
        )

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
            detail="TikTok token exchange failed",
        )

    token_data = response.json()

    db = SessionLocal()

    try:

        account = db.query(TikTokAccount).filter(
            TikTokAccount.open_id == token_data["open_id"]
        ).first()

        if account is None:

            account = TikTokAccount(
                open_id=token_data["open_id"],
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_in=token_data["expires_in"],
                refresh_expires_in=token_data["refresh_expires_in"],
                scope=token_data["scope"],
                token_type=token_data["token_type"],
            )

            db.add(account)

        else:

            account.access_token = token_data["access_token"]
            account.refresh_token = token_data["refresh_token"]
            account.expires_in = token_data["expires_in"]
            account.refresh_expires_in = token_data["refresh_expires_in"]
            account.scope = token_data["scope"]
            account.token_type = token_data["token_type"]

        print("[TIKTOK] BEFORE COMMIT")
        print(f"[TIKTOK] open_id = {account.open_id}")

        db.commit()

        print("[TIKTOK] AFTER COMMIT")

        return {
            "success": True,
            "message": "TikTok account connected successfully",
            "open_id": token_data["open_id"],
        }

    finally:
        db.close()

@app.get("/debug/tiktok")
def debug_tiktok():

    db = SessionLocal()

    try:
        account = db.query(TikTokAccount).first()

        if account is None:
            return {
                "connected": False
            }

        return {
            "connected": True,
            "open_id": account.open_id,
            "scope": account.scope,
            "token_type": account.token_type,
            "has_access_token": bool(account.access_token),
            "has_refresh_token": bool(account.refresh_token),
        }

    finally:
        db.close()