import os
import time

import requests

from sqlalchemy.orm import Session

from .models import TikTokAccount


TIKTOK_CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
TIKTOK_CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")


def refresh_access_token(
    db: Session,
    account: TikTokAccount,
) -> str:

    response = requests.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data={
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": account.refresh_token,
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"TikTok token refresh failed: {response.text}"
        )

    token_data = response.json()

    account.access_token = token_data["access_token"]
    account.refresh_token = token_data["refresh_token"]

    account.expires_in = token_data["expires_in"]
    account.refresh_expires_in = token_data["refresh_expires_in"]

    account.token_type = token_data["token_type"]

    if "scope" in token_data:
        account.scope = token_data["scope"]

    db.commit()

    return account.access_token