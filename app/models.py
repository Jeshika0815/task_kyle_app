from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Text, DateTime, ForeignKey, relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=True, index=True)
    google_sub = Column(String, unique=True, index=True, nullable=True)

    #Calendar connect(If not connect then. It's all null.)
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    google_token_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="events")
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
    departure = Column(Boolean)
    departure_time = Column(Time)
    memo = Column(Text)
