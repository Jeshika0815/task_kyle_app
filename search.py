#これはdbに入っているデータを確認するためのコマンドですね。
from datetime import date, time
from db import SessionLocal 
from models import Event     

session = SessionLocal()

#データの中身を表示するためのコード
all_events = session.query(Event).all()

for event in all_events:
    print(f"ID: {event.id} | 予定名: {event.plan_name} | 日付: {event.start_date} | 場所: {event.location}")

print("---------------------------------------------------\n")



session.close()
