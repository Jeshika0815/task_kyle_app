from datetime import date, time, datetime
from db import SessionLocal  # セッション（接続）をインポート
from models import Event     # 定義したEventモデルをインポート

# データベースセッションを開始
session = SessionLocal()

print("===  予定の新規登録 ===")

# 1. ユーザーからの入力を受け取る
plan_name = input("予定名を入力してください: ")

# 日付の入力
start_date_str = input("開始日を入力してください (例: 2026-07-10): ")
start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

finish_date_str = input("終了日を入力してください (例: 2026-07-10): ")
finish_date = datetime.strptime(finish_date_str, "%Y-%m-%d").date()

# 時間の入力と変換 (例: 14:00 と入力してもらう)
start_time_str = input("開始時間を入力してください (例: 14:00): ")
start_time = datetime.strptime(start_time_str, "%H:%M").time()

finish_time_str = input("終了時間を入力してください (例: 15:30): ")
finish_time = datetime.strptime(finish_time_str, "%H:%M").time()

# アラーム設定 (yes なら True、それ以外は False)
alarm_input = input("アラームを設定しますか？ (yes/no): ")
alarm = True if alarm_input.lower() == 'yes' else False

repeats = input("繰り返し設定 (例: なし、毎週、毎月): ")
tags = input("タグ (例: 仕事, プライベート): ")
location = input("場所 (例: 会議室A、自宅): ")
url = input("URL (例: Zoomのリンクなど): ")
memo = input("メモ・詳細: ")


# 2. 入力されたデータを使ってEventオブジェクトを作成
new_event = Event(
    plan_name=plan_name,
    start_date=start_date,
    finish_date=finish_date,
    start_time=start_time,
    finish_time=finish_time,
    alarm=alarm,
    repeats=repeats,
    tags=tags,
    location=location,
    url=url,
    memo=memo
)

# 3. データベースに追加して確定
session.add(new_event)
session.commit()

print(f"\n 新しいタスク「{new_event.plan_name}」をデータベースに追加しました！ID: {new_event.id}")

# セッションを閉じる
session.close()
