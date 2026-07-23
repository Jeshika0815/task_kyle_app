#schemas.py
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional
from datetime import date, datetime, time

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
    start_date: date | None = None
    finish_date: date | None = None

class TimeSchema(BaseModel):
    start_time: time | None = None
    finish_time: time | None = None

class Plans(BaseModel):
    plan_name: str
    date: DateSchema
    time: TimeSchema
    alarm: bool = False
    repeats: str | None = None
    tags: list[str] = []
    location: str | None = None
    url: str | None = None
    memo: str | None = None

class EventCreate(Plans):
    id: int
    departure: datetime | None = None
