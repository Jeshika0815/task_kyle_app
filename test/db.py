#実行はプロジェクトルートから `python -m test.db` で行ってください
from datetime import date, time
from app.database import SessionLocal  # セッション（接続）をインポート
from app.models import Event           # 定義したEventモデルをインポート

# データベースセッションを開始
session = SessionLocal()

# 新しいのデータテーブルを作成
new_event = Event(
    plan_name="プロジェクト打ち合わせ",
    start_date=date(2026, 7, 10),      # 年、月、日
    finish_date=date(2026, 7, 10),
    start_time=time(14, 0),            # 時、分
    finish_time=time(15, 30),
    alarm=True,
    repeats="なし",
    tags=["仕事", "ミーティング"],
    location="会議室A",
    url="https://example.com/zoom",
    memo="資料を事前に確認しておくこと。"
)

# データベースに追加して確定（コミット）
session.add(new_event)
session.commit()

print(f"タスク「{new_event.plan_name}」を追加しました。ID: {new_event.id}")
session.close()
