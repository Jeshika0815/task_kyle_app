#schemas.py
from pydantic import BaseModel

class EventCreate(BaseModel):
  
    plan_name: str
    start_date: str
    finish_date: str
    start_time: str
    finish_time: str
    alarm: bool = False
    repeats: str | None = None
    tags: str | None = None  
    location: str | None = None
    url: str | None = None
    memo: str | None = None

    class Config:
        from_attributes = True
