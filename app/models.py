from sqlalchemy import Column, Integer, String, Boolean, Date, Time, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    events = relationship("Events", back_populates="user")
    clients = relationship("Clients", back_populates="user")
    api_sessions = relationship("APISessions", back_populates="user")
    oauth_tokens = relationship("OAuthToken", back_populates="user")

class Events(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    google_event_id = Column(String, nullable=True)
    user = relationship("Users", back_populates="events")
    plan_name = Column(String)
    start_date = Column(Date)
    finish_date = Column(Date)
    start_time = Column(Time)
    finish_time = Column(Time)
    alarm = Column(Boolean)
    repeats = Column(String)
    _tags = Column("tags", Text)
    location = Column(String)
    url = Column(String)
    departure = Column(DateTime)
    departure_check = Column(Boolean, default=False)
    memo = Column(Text)

    # schemas.Plans expects date/time as nested {start_*, finish_*} objects
    # and tags as a list[str], but the table stores them as flat columns /
    # a comma-joined string. These bridge the two shapes for (de)serialization.
    @property
    def date(self):
        return {"start_date": self.start_date, "finish_date": self.finish_date}

    @property
    def time(self):
        return {"start_time": self.start_time, "finish_time": self.finish_time}

    @property
    def tags(self):
        return self._tags.split(",") if self._tags else []

    @tags.setter
    def tags(self, value):
        self._tags = ",".join(value) if value else None

# For holding what users have connected to other services
class Clients(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("Users", back_populates="clients")
    client_name = Column(String, nullable=False)

# For holding other service connect service sessions
class APISessions(Base):
    __tablename__ = "api_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("Users", back_populates="api_sessions")
    jwt_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    token_expiry = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# For holding OAuth token information
class OAuthToken(Base):
    __tablename__ = "oauth_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    #Calendar connect(If not connect then. It's all null.)
    provider = Column(String, nullable=False, default="google")
    provider_sub = Column(String, nullable=False, index=True)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    token_expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("Users", back_populates="oauth_tokens")

    __table_args__ = (
        UniqueConstraint("provider", "provider_sub", name="uq_provider_identity"),
        UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )
