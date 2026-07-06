#dbに入っている中身を表示するためのコードです
from datetime import date, time
from db import SessionLocal  # セッション（接続）をインポート
from models import Event     # 定義したEventモデルをインポート

# データベースセッションを開始
session = SessionLocal()

# データベースからイベントを取得する
all_events = session.query(Event).all()

# for文を使って、1件ずつ表示させる
for event in all_events:
    print(f"ID: {event.id} | 予定名: {event.plan_name} | 日付: {event.start_date} | 場所: {event.location}")

print("---------------------------------------------------\n")


# 4. セッションを閉じる
session.close()
