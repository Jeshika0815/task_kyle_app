import os
import requests
from sqlalchemy.orm import Session
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token as google_id_token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GRequest
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/user.addresses.read"
]

MAP_KEY = os.environ.get("MAP_API")

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



# -- calendar crud --
def _gcalendar_event_body(event):
    start_dt = datetime.combine(event.start_date, event.start_time)
    end_dt = datetime.combine(event.finish_date, event.finish_time)
    return {
        "summary": event.plan_name,
        "location": event.location,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Tokyo"},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Tokyo"},
    }

def add_event(user, event) -> str:
    service = build_calendar_service(user)
    created = service.events().insert(calendarId="primary", body=_gcalendar_event_body(event)).execute()
    return created["id"]

def show_events(user, event):
    service = build_calendar_service(user)
    events = service.events().get(calendarId="primary", eventId=event.google_event_id).execute()
    return events

def update_event(user, event):
    service = build_calendar_service(user)
    service.events().update(calendarId="primary", eventId=event.google_event_id, body=_gcalendar_event_body(event)).execute()

def delete_event(user, event):
    service = build_calendar_service(user)
    service.events().delete(calendarId="primary", eventId=event.google_event_id).execute()

# -- build service relation --
def _build_credentials(user) -> Credentials:
    token_raw = _get_gtoken(user)
    if token_raw is None:
        raise ValueError("Google Calendar is not connected")
    creds = Credentials(
        token=token_raw.access_token,
        refresh_token=token_raw.refresh_token,
        token_uri=os.environ["CLIENT_TOKEN_URI"],
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        scopes=SCOPES
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(GRequest())
    return creds

def build_people_service(user):
    return build("people", "v1", credentials=_build_credentials(user))

# -- departure management --
# get your home address
def get_your_address(user: int) -> str | None:
    # Create Credentials
    peoples = build_people_service(user) # Create People API Service
    profile = peoples.people().get(resourceName='people/me', personFields='addresses').execute()
    addresses = profile.get('addresses', [])
    # Search for the your home address
    for addr in addresses:
        if addr.get('type') == 'home':
            return addr.get('formattedValue')
    # Not registed home your address
    return None

# get travel time
def get_traveltime(origin: str, destination: str, travel_mode: str = "TRANSIT") -> int:
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": MAP_KEY,
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters" # FieldMask to reduce response size
    }
    payload = {
        "origin": {"address": origin},
        "destination": {"address": destination},
        "travelMode": travel_mode,
        "LanguageCode": "ja-JP"
    }
    res = requests.post(url, json=payload, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Map API Error: {res.text}")

    data = res.json()
    if not data.get("routes"):
        raise Exception("Not found route. Please check the origin and destination.")
    duration_str = data["routes"][0]["duration"]
    duration_seconds = int(duration_str.replace("s", ""))
    return duration_seconds

def calc_departures(user, event) -> datetime | None:
    if not event.location:
        return None

    origin = get_your_address(user)

    if not origin:
        return None

    start_dt = datetime.combine(event.start_date, event.start_time)
    try:
        travel_time = get_traveltime(origin, event.location)
    except Exception:
        return None
    return start_dt - timedelta(seconds=travel_time)
