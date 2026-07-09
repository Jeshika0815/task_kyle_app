#schemas.py
from datetime import date, time
from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class CreateUser(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    id: int | None = None
    plan_name: str
    start_date: date
    finish_date: date | None = None
    start_time: time
    finish_time: time | None = None
    alarm: bool = False
    repeats: str | None = None
    tags: list[str] = []
    location: str | None = None
    url: str | None = None
    departure: bool = False
    departure_time: time | None = None
    memo: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EventCreate(EventBase):
    pass
