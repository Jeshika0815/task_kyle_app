# やることは, Google Calendarの制御(接続, 取得, 作成, 編集, 削除)と出発アラートの記述(書き終わったら消す)
import os
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token as google_id_token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GRequest
from googleapiclient.discovery import build

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
]

# connect google calendar and refer that
def _client_conf() -> dict:
    return {
        "web": {
            "client_id": os.environ["CLIENT_ID"],
            "client_secret": os.environ["CLIENT_SECRET"],
            "auth_uri": os.environ["CLIENT_AUTH_URI"],
            "token_uri": os.environ["CLIENT_TOKEN_URI"],
            "redirect_uri": os.environ["ENDPOINT"]
        }
    }

def get_authorization_url(state: str) -> str:
    flow = Flow.from_client_config(_client_conf(), scopes=SCOPES)
    flow.redirect_uri = os.environ["ENDPOINT"]
    auth_url, _ = flow.authorization_url(
        access_type="offline", # refresh_tokenを取得するため用
        include_granted_scopes=True,
        prompt="consent", # ユーザに対して毎回同意を求め, refresh_tokenを確実に取得
    )
    return auth_url

def exchange_code(code: str):
    flow = Flow.from_client_config(_client_conf(), scopes=SCOPES)
    flow.redirect_uri = os.environ["ENDPOINT"]
    flow.fetch_token(code=code)
    creds = flow.credentials

    id_info = google_id_token.verify_oauth2_token(creds.id_token, google_requests.Request(), os.environ["CLIENT_ID"])
    return creds, id_info

# get Google token from user's OAuth tokens
def _get_gtoken(user):
    return next((t for t in user.oauth_tokens if t.provider == "google"), None)

def build_calendar_service(user):
    token_raw = _get_gtoken(user)
    if token_raw is None:
        raise ValueError("Google Calendar is not connected for you")
    creds = Credentials(
        token=token_raw.access_token,
        refresh_token=token_raw.refresh_token,
        token_uri=os.environ["CLIENT_TOKEN_URI"],
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(GRequest())
    return build("calendar", "v3", credentials=creds)

# check connection between application and Google Calendar
def is_connected(user) -> bool:
    return _get_gtoken(user) is not None

# -- departure management --
def departures():
    pass
