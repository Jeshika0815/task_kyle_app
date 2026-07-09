# models.py
from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Text
from database import Base

class Event(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    plan_name = Column(String)

    start_date = Column(Date)

    finish_date = Column(Date)

    start_time = Column(Time)

    finish_time = Column(Time)

    alarm = Column(Boolean)

    repeats = Column(String)

    tags = Column(Text)

    location = Column(String)

    url = Column(String)

    memo = Column(Text)

task= Event
