from datetime import date, time, datetime
from database import SessionLocal, engine  
from models import Event, Base             

# 入力する前データベースにテーブルを自動作成する
Base.metadata.create_all(bind=engine)

session = SessionLocal()

print("===　タスク登録　===")

fixed_plan_name   = "固定のプロジェクト打ち合わせ"
fixed_start_date  = date(2026, 7, 10)       # 年、月、日
fixed_finish_date = date(2026, 7, 10)
fixed_start_time  = time(14, 0)             # 時、分
fixed_finish_time = time(15, 30)
fixed_alarm       = True                     # True または False
fixed_repeats     = "なし"
fixed_tags        = "仕事, ミーティング"
fixed_location    = "会議室A"
fixed_url         = "https://example.com/zoom"
fixed_memo        = "資料を事前に確認しておくこと。"


# 決めたデータを使ってオブジェクトを作成
new_event = Event(
    plan_name=fixed_plan_name,
    start_date=fixed_start_date,
    finish_date=fixed_finish_date,
    start_time=fixed_start_time,
    finish_time=fixed_finish_time,
    alarm=fixed_alarm,
    repeats=fixed_repeats,
    tags=fixed_tags,
    location=fixed_location,
    url=fixed_url,
    memo=fixed_memo
)

# データベースに追加して確定（コミット）
session.add(new_event)
session.commit()

print(f"\n新しいタスク「{new_event.plan_name}」を追加しました！ID: {new_event.id}")

session.close()
