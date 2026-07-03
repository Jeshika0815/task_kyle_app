#schemas.py
from pydantic import BaseModel

class DateSchema(BaseModel):
    start_date: str
    finish_date: str

class TimeSchema(BaseModel):
    start_time: str
    finish_time: str

class EventCreate(BaseModel):

    plan_name: str

    date: DateSchema

    time: TimeSchema

    alarm: bool = False

    repeats: str | None = None

    tags: list[str] = []

    location: str | None = None

    url: str | None = None

    memo: str | None = None
