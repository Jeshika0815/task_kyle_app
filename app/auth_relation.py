import jwt
import os
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models import Users, OAuthToken
from .database import get_db
from . import calender_relation

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
ISSUER = os.environ.get("ISSUER")
AUDIENCE = os.environ.get("AUDIENCE")

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ENDPOINT = os.environ.get("ENDPOINT")

# Get access token and refresh token at Google OAuth(at first registration)
def save_oauth_tokens(user, token, db) -> bool:
    # Save tokens in database
    try:
        db_oauth = OAuthToken(user_id=user.id, access_token=token.access_token, refresh_token=token.refresh_token, token_expiry=token.expires_at)
        db.add(db_oauth)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save OAuth tokens:{e}")
        return False

# Create local JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.now()
    to_encode.update({
        "iat": now,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": now
    })
    if expires_delta:
        to_encode.update({
            "exp": now + expires_delta
        })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Authenticate user
def authenticate_user(db: Session, email: str, password: str) -> Users | None:
    user = db.query(Users).filter(Users.email == email).first()
    if user and pwd_context.verify(password, user.password):
        return user
    return None

# Verify Authentication
def auth_verification(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) ) -> Users | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={"verify_signature": True, "verify_exp": True, "verify_iss": True, "verify_aud": True, "require":["exp", "iss", "aud"]}
        )
        user = db.query(Users).filter(Users.email == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}) from  e
    return None

# Connect oauth2
def connect_goauth(code: str | None = None, db: Session = Depends(get_db)):
    creds, id_info = calender_relation.exchange_code(code)
    token_row = (db.query(OAuthToken).filter(OAuthToken.provider == "google", OAuthToken.provider_sub == id_info["sub"]).first())
    if token_row:
        user = token_row.user
    else:
        user = db.query(Users).filter(Users.email == id_info["email"]).first()
        if not user:
            user = Users(
                email=id_info["email"],
                password=None,
            )
            db.add(user)
            db.flush()
        token_row = OAuthToken(user_id=user.id, provider="google", provider_sub=id_info["sub"], access_token=creds.token, refresh_token=creds.refresh_token, token_expiry=creds.expiry)
        db.add(token_row)

    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.email, "iss": ISSUER, "aud": AUDIENCE}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return token


# search for a user by email
def get_user(db: Session, email: str) -> Users | None:
    return db.query(Users).filter(Users.email == email).first()

# registlation
def register(db: Session, email: str, password: str) -> Users:
    user = get_user(db, email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user is already registered")
    return create_user(db, email, password)

def create_user(db: Session, email: str, password: str) -> Users | None:
    hashed_password = pwd_context.hash(password)
    user = Users(email=email, password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
