from app import calender_relation
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import schemas
from ..database import get_db
from .. import auth_relation


router = APIRouter(prefix = "/auth", tags = ["auth"])

# Login endpoint
@router.post("/login", response_model=schemas.Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_relation.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    token = auth_relation.create_access_token({"sub": user.email, "iss": auth_relation.ISSUER, "aud": auth_relation.AUDIENCE}, expires_delta=timedelta(minutes=auth_relation.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": token, "token_type": "bearer"}

# Register endpoint
@router.post("/register", response_model=schemas.CreateUser)
async def register(payloads: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    user = auth_relation.register(db, payloads.user.email, payloads.user.password.get_secret_value())
    if payloads.user.confirm_oauth:
        if not payloads.oauth_tokens:
            raise HTTPException(status_code=400, detail="Failed to link Google OAuth")
        success = auth_relation.save_oauth_tokens(user, payloads.oauth_tokens, db)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save OAuth tokens")
    return user

@router.get("/google")
async def google_auth(code: str | None = None, db: Session = Depends(get_db)):
    if code is None:
        return RedirectResponse(calender_relation.get_authorization_url(state=""))
    token = auth_relation.connect_goauth(code, db)
    return {"access_token": token, "token_type": "bearer"}
