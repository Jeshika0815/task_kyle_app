from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .database import Base, engine
from . import models  # noqa: F401  registers Event/User on Base.metadata before create_all
from .routers import auth, tasks, prompt_organize


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(prompt_organize.router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI in Docker!"}
