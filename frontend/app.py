
NFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Traceback (most recent call last):
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\multiprocessing\process.py", line 313, in _bootstrap
    self.run()
    ~~~~~~~~^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\multiprocessing\process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
    ~~~~~~^^^^^^^^^^^^^^^^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\server.py", line 75, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 196, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 119, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\base_events.py", line 725, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\server.py", line 79, in serve
    await self._serve(sockets)
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\server.py", line 86, in _serve
    config.load()
    ~~~~~~~~~~~^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\config.py", line 441, in load
    self.loaded_app = import_from_string(self.app)
                      ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\uvicorn\importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1395, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1023, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\KZ2MS\PROJECTS2\Projects\JNZ\Kojima_apps\front\app.py", line 90, in <module>
    client.run(TOKEN)
    ~~~~~~~~~~^^^^^^^
  File "C:\Users\KZ2MS\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\discord\client.py", line 933, in run
    asyncio.run(runner())
    ~~~~~~~~~~~^^^^^^^^^^
  File "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\Lib\asyncio\runners.py", line 192, in run
    raise RuntimeError(
        "asyncio.run() cannot be called from a running event loop")
RuntimeError: asyncio.run() cannot be called from a running event loop
<sys>:0: RuntimeWarning: coroutine 'Client.run.<locals>.runner' was never awaited
RuntimeWarning: Enable tracemalloc to get the object allocation traceback

原因はこれ。

RuntimeError: asyncio.run() cannot be called from a running event loop

つまり、

Uvicorn(FastAPI) が既に asyncio のイベントループを動かしている
その中で discord.Client.run() を呼んだ
client.run() は内部で asyncio.run() を実行する
イベントループを二重起動しようとして落ちた
app.pyを見ると
app = FastAPI()

...

client.run(TOKEN)   ← これ

となっているはず。

これはFastAPIではやってはいけない。

方法1（おすすめ）

client.start() を使う。

@app.on_event("startup")
async def startup():
    asyncio.create_task(client.start(TOKEN))

そして

client.run(TOKEN)

は削除。

方法2（もっとおすすめ）

Discord BotとFastAPIを別プロセスにする。

bot.py
client.run(TOKEN)
api.py
uvicorn.run(app)

起動

python bot.py
python api.py

これが一番綺麗。

方法3

一つのイベントループで動かす。

import asyncio
import uvicorn

async def main():
    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=8000)
    )

    await asyncio.gather(
        client.start(TOKEN),
        server.serve(),
    )

asyncio.run(main())

これなら両方同じループで動く。

今回のエラーの直接原因

ログを見ると

File "app.py", line 90

client.run(TOKEN)

これが原因。

uvicorn app:app --reload で起動すると、

Uvicorn
 ↓
 asyncio.run(...)
      ↓
 app.py読み込み
      ↓
 client.run()
      ↓
 asyncio.run() ← 二回目

となって死んでいる。

以前「DiscordからFastAPIへ値を渡すだけならPythonを分けた方がいい」と話していた構成なら、bot.py と api.py を分離するのが一番シンプルで保守もしやすい。

もし app.py のコード全体を貼ってくれれば、「最小限の修正」で動く形に書き換えるよ。

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
