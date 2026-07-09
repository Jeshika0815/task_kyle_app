from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import schemas
from ..database import get_db
from .. import auth_relation

router = APIRouter(prefix = "/auth", tags = ["auth"])

def _issue_token(email: str) -> dict:
    token = auth_relation.create_access_token(
        {"sub": email},
        expires_delta=timedelta(minutes=int(auth_relation.ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_relation.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return _issue_token(user.email)

@router.post("/register", response_model=schemas.Token)
async def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    registered = auth_relation.RegisterUser(user.email, user.password).register(db)
    return _issue_token(registered.email)
