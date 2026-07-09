from fastapi import FastAPI
from .routers import auth, tasks, prompt_organize
from sqlalchemy.orm import Session



app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(prompt_organize.router)

@app.get("/")
def read_root():
	return {"message": "Hello from FastAPI in Docker!"}
