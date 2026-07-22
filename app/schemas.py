#schemas.py
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional
from datetime import datetime

class GOauthTokens(BaseModel):
    id: int
    user_id: int
    access_token: Optional[str] = None
    refresh_token: Optional[str]=None
    expires_at: Optional[datetime] = None

class CreateUser(BaseModel):
    id: int
    email: EmailStr
    name: str | None = None
    password: SecretStr
    confirm_oauth: bool = False

class UserRegisterRequest(BaseModel):
    user: CreateUser
    oauth_tokens: Optional[GOauthTokens] = None

class Token(BaseModel):
    token_type: str = "bearer"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class DateSchema(BaseModel):
    start_date: str
    finish_date: str

class TimeSchema(BaseModel):
    start_time: str
    finish_time: str

class EventCreate(BaseModel):
    id: int
    plan_name: str
    date: DateSchema
    time: TimeSchema
    alarm: bool = False
    repeats: str | None = None
    tags: list[str] = []
    location: str | None = None
    url: str | None = None
    departure: datetime | None = None
    memo: str | None = None
