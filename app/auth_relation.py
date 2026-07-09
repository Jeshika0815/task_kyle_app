import httpx
import jwt
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from .database import get_db
from .models import User


oauth_api = "https://oauth2.googleapis.com"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ENDPOINT = os.environ.get("ENDPOINT")

# Dependency
def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

async def exchange_code(code: str, code_verifier: str, client: httpx.AsyncClient) -> dict:
    payloads = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": f"{ENDPOINT}/auth/google/callback",
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }
    try:
        response = await client.post(f"{oauth_api}/token", data=payloads)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        # Google OAuth2 API error relation
        except_detail = e.response.json() if e.response.headers.get("content-type") == "application/json" else e.response.text
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google Oauth error:{except_detail}")

    except httpx.RequestError as e:
        # Network error or timeout relation
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Network error occurred while contacting Google: {e}")

# For ID token verification via google oauth2 (Google Sign-In only)
def token_verification(id_token: str, client: httpx.AsyncClient) -> dict:

    try:
        user_info = google_id_token.verify_oauth2_token(id_token, google_requests(), CLIENT_ID)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token verification failed:{e}")

    # minimal security check(the token deriver correct place(my application))
    if user_info.get("aud") != CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not match the client ID")

    # iss verification
    if user_info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not match the issuer")

    return user_info

# Create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verifies our own JWT (issued by /auth/login or /auth/register) sent as a
# Bearer token, and returns the corresponding user. This protects /task and
# /prompt_ctl routes.
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Authenticate user
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user and pwd_context.verify(password, user.password):
        return user
    return None

# registlation
class RegisterUser:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def get_email(self) -> str:
        return self.email

    def get_user_by_email(self, db: Session) -> User | None:
        return db.query(User).filter(User.email == self.email).first()

    def register(self, db: Session) -> User:
        user = self.get_user_by_email(db)
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user is already registered")
        return self.create_user(db, self.email, self.password)

    def create_user(self, db: Session, email: str, password: str) -> User | None:
        hashed_password = pwd_context.hash(password)
        user = User(email=email, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
