#schemas.py
from pydantic import BaseModel

class EventCreate(BaseModel):
    # 他のファイル（tasks.py等）が構造に修正しました
    plan_name: str
    start_date: str
    finish_date: str
    start_time: str
    finish_time: str
    alarm: bool = False
    repeats: str | None = None
    tags: str | None = None  # models.pyのText型に合わせて文字列(str)にしています
    location: str | None = None
    url: str | None = None
    memo: str | None = None

    class Config:
        # 念のため、ORM（SQLAlchemy）のモデルと相互変換できるように有効化しておきます
        from_attributes = True
