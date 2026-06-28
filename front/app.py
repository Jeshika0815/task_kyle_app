from fastapi import FastAPI
import requests
from dotenv import load_dotenv
import os
from pydantic import BaseModel

app = FastAPI()

load_dotenv()

GAS_URL = os.getenv("GAS_URL")

class ScheduleRequest(BaseModel):
    start: str
    end: str
    date: str
    time: str

@app.post("/schedule")
def schedule(req: ScheduleRequest):

    payload = {
        "start": req.start,
        "end": req.end,
        "date": req.date,
        "time": req.time
    }

    res = requests.post(
        GAS_URL,
        json=payload
    )

    return res.json()
