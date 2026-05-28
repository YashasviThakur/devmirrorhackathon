"""
DevMirror — Google OAuth2 authentication router.
Handles the full login loop: /login redirect → Google → /callback → DB upsert → frontend redirect.
Also exposes refresh_google_token_if_needed() as a reusable utility for all protected endpoints.
"""

import os
import json
import base64
import logging
from datetime import datetime, timedelta
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from models import User, LinkedAccount, get_db

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI  = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/api/auth/google/callback",
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

GOOGLE_AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/youtube.readonly",
]


# ── State encoding helpers ─────────────────────────────────────────────────────

def _encode_state(account_type: str, institution_name: Optional[str]) -> str:
    payload = json.dumps({
        "account_type": account_type,
        "institution_name": institution_name or "",
    })
    return base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")


def _decode_state(state: str) -> dict:
    padded = state + "=" * (-len(state) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())


# ── Login redirect ─────────────────────────────────────────────────────────────

@router.get("/api/auth/google/login")
async def google_login(
    account_type: str = Query("personal"),
    institution_name: Optional[str] = Query(None),
):
    """
    Builds a Google OAuth2 authorization URL requesting all required scopes,
    serialises account_type and institution_name into the state parameter,
    and issues an HTTP 302 redirect to Google.
    """
    if account_type not in ("personal", "institution"):
        raise HTTPException(
            status_code=400,
            detail="account_type must be 'personal' or 'institution'",
        )

    if not GOOGLE_CLIENT_ID:
        logger.error("GOOGLE_CLIENT_ID not configured")
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    state = _encode_state(account_type, institution_name)
    logger.info(f"Initiating Google OAuth login for {account_type} account")

    params = {
        "client_id":              GOOGLE_CLIENT_ID,
        "redirect_uri":           GOOGLE_REDIRECT_URI,
        "response_type":          "code",
        "scope":                  " ".join(SCOPES),
        "access_type":            "offline",
        "prompt":                 "consent",
        "include_granted_scopes": "true",
        "state":                  state,
    }

    qs = "&".join(
        f"{k}={requests.utils.quote(str(v), safe='')}"
        for k, v in params.items()
    )
    auth_url = f"{GOOGLE_AUTH_BASE}?{qs}"
    logger.info(f"Redirecting to Google OAuth URL")
    return RedirectResponse(url=auth_url)


# ── OAuth2 callback ────────────────────────────────────────────────────────────

@router.get("/api/auth/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Google redirects here after user consent.
    1. Decode state to recover account_type / institution_name.
    2. Exchange authorization code for access + refresh tokens.
    3. Fetch user email via userinfo endpoint.
    4. Upsert User + LinkedAccount rows in the database.
    5. Redirect the browser to the frontend dashboard.
    """
    # Check for Google OAuth errors
    if error:
        logger.error(f"Google OAuth error: {error}")
        raise HTTPException(
            status_code=400,
            detail=f"Google authentication failed: {error}",
        )

    logger.info("Received Google OAuth callback")

    try:
        state_data       = _decode_state(state)
        account_type     = state_data.get("account_type", "personal")
        institution_name = state_data.get("institution_name") or None
    except Exception as e:
        logger.error(f"Failed to decode state: {e}")
        account_type     = "personal"
        institution_name = None

    # Exchange code for tokens
    logger.info("Exchanging authorization code for tokens")
    token_resp = requests.post(
        GOOGLE_TOKEN_URL,
        data={
            "code":          code,
            "client_id":     GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri":  GOOGLE_REDIRECT_URI,
            "grant_type":    "authorization_code",
        },
        timeout=10,
    )
    if token_resp.status_code != 200:
        logger.error(f"Token exchange failed: {token_resp.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Google token exchange failed: {token_resp.text}",
        )

    token_data    = token_resp.json()
    access_token  = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in    = token_data.get("expires_in", 3600)
    scope         = token_data.get("scope", "")
    expiry        = datetime.utcnow() + timedelta(seconds=expires_in)

    # Resolve user email
    logger.info("Fetching user info from Google")
    userinfo_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    if userinfo_resp.status_code != 200:
        logger.error(f"Failed to fetch user info: {userinfo_resp.text}")
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch user info from Google",
        )
    userinfo = userinfo_resp.json()
    email = userinfo.get("email")
    if not email:
        logger.error("Google did not return an email address")
        raise HTTPException(status_code=400, detail="Google did not return an email address")

    logger.info(f"Successfully authenticated user: {email}")

    # Upsert User row
    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.info(f"Creating new user: {email}")
        user = User(
            email=email,
            account_type=account_type,
            institution_name=institution_name,
        )
        db.add(user)
        db.flush()
    else:
        logger.info(f"Found existing user: {email}")
        user.account_type = account_type
        if institution_name:
            user.institution_name = institution_name

    # Upsert LinkedAccount row
    linked = user.linked_accounts
    if not linked:
        linked = LinkedAccount(user_id=user.id)
        db.add(linked)
        db.flush()

    linked.google_access_token = access_token
    if refresh_token:
        linked.google_refresh_token = refresh_token
    linked.google_token_scope  = scope
    linked.google_token_expiry = expiry

    db.commit()
    db.refresh(user)

    logger.info(f"Auth complete for user {user.id}, redirecting to dashboard")
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard?user_id={user.id}")


# ── Token refresh utility ──────────────────────────────────────────────────────

def refresh_google_token_if_needed(user_id: int, db: Session) -> Optional[str]:
    """
    Returns a valid Google access token for the given user.
    Tokens within 5 minutes of expiry are proactively refreshed via the
    refresh token and the updated value is persisted to the database.
    Returns None if no valid token can be obtained.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.linked_accounts:
        return None

    linked        = user.linked_accounts
    access_token  = linked.google_access_token
    refresh_token = linked.google_refresh_token
    expiry        = linked.google_token_expiry
    now           = datetime.utcnow()

    token_expired = (
        access_token is None
        or (expiry is not None and expiry <= now + timedelta(minutes=5))
    )

    if token_expired and refresh_token:
        resp = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id":     GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type":    "refresh_token",
            },
            timeout=10,
        )
        if resp.status_code == 200:
            data                       = resp.json()
            linked.google_access_token = data["access_token"]
            linked.google_token_expiry = now + timedelta(
                seconds=data.get("expires_in", 3600)
            )
            db.commit()
            return data["access_token"]
        return None

    return access_token
