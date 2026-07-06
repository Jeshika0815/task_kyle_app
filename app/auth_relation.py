import httpx
from fastapi import HTTPException, status
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests



clientd = httpx.AsyncClient()
oauth_api = "https://oauth2.googleapis.com"

# Dependency
def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

async def exchange_code(code: str, code_verifier: str, client: httpx.AsyncClient) -> dict:
    payloads = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": APP_CALLBACK_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }
    try:
        response = await clientd.post(f"{oauth_api}/token", data=payloads)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # Google OAuth2 API error relation

        except_detail = e.response.json() if e.response.headers.get("content-type") == "application/json" else e.response.text
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google Oauth error:{except_detail}")

    except httpx.RequestError as e:
        # Network error or timeout relation
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Network error occurred while contacting Google: {e}")

# For ID token verification via google oauth2
async def token_verification(id_token: str, client: httpx.AsyncClient) -> dict:

    try:
        user_info = await google_id_token.verify_oauth2_token(id_token, google_requests(), CLIENT_ID)
    except httpx.ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification failed:{e}")

    # minimal security check(the token deriver correct place(my application))
    if user_info.get("aud") != CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not match the client ID")

    # iss verification
    if user_info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not match the issuer")

    return user_info
