#schemas.py
from pydantic import BaseModel

class DateSchema(BaseModel):
    start_date: str
    finish_date: str

class TimeSchema(BaseModel):
    start_time: str
    finish_time: str

class EventBase(BaseModel):
    task_id: int | None = None
    plan_name: str
    date: DateSchema
    time: TimeSchema
    alarm: bool = False
    repeats: str | None = None
    tags: list[str] = []
    location: str | None = None
    url: str | None = None
    departure: bool = False
    departure_time: str | None = None
    memo: str | None = None

class EventCreate(EventBase):
    pass
