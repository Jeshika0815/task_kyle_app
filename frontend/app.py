import os
import threading
import requests
import discord

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

load_dotenv()

SCHEDULE_GAS_URL = os.getenv("SCHEDULE_GAS_URL")
DISCORD_GAS_URL = os.getenv("DISCORD_GAS_URL")
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# ------------------------
# FastAPI
# ------------------------

app = FastAPI()

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

    res = requests.post(SCHEDULE_GAS_URL, json=payload)

    return res.json()

# ------------------------
# Discord Bot
# ------------------------

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id != CHANNEL_ID:
        return

    try:
        response = requests.post(
            DISCORD_GAS_URL,
            json={
                "message": message.content,
                "user": message.author.name
            }
        )

        await message.reply(response.json()["reply"])

    except Exception as e:
        print(e)
        await message.reply("Webhook通信エラー")

# ------------------------
# 並列起動
# ------------------------

def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

client.run(TOKEN)
