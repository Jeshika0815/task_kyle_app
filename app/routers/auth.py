from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db
from .. import auth_relation

router = APIRouter(prefix = "/auth", tags = ["auth"])

@router.post("/login", response_model=schemas.Token)
async def login(db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = auth_relation.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.CreateUser)
async def register(user: schemas.CreateUser, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)
