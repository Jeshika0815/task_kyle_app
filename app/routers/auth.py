from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import schemas
from ..database import get_db
from .. import auth_relation

router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.post("/login", response_model=schemas.Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_relation.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = auth_relation.create_access_token({"sub": user.email}, expires_delta=timedelta(minutes=int(auth_relation.ACCESS_TOKEN_EXPIRE_MINUTES)))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.CreateUser)
async def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    db_user = auth_relation.RegisterUser.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth_relation.RegisterUser.register(db, user.email)
