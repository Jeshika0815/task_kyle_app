from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DB_INFO = f"postgresql://{os.environ['DBUSER']}:{os.environ['ROOTPASS']}@{os.environ['DBHOST']}:{os.environ['DBPORT']}/{os.environ['DATABASE']}"

engine = create_engine(DB_INFO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
