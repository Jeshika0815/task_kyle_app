from fastapi import FastAPI
from .routers import auth, tasks, prompt_organize
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db


app = FastAPI()

# Create tables that don't exist yet (no migration tooling in this project).
models.Base.metadata.create_all(bind=engine)

# For testing(Database Simulation)
DB={}

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(prompt_organize.router)

@app.get("/")
def read_root():
	return {"message": "Hello from FastAPI in Docker!"}
