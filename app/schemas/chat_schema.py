from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

# 回傳給前端的訊息格式
class MessageRead(BaseModel):
    id: int
    sender_id: str  # 資料庫是 UUID，這裡定義為 str
    content: str
    created_at: datetime

    # 👇 關鍵修正：使用 ConfigDict 來設定
    model_config = ConfigDict(
        from_attributes=True,  # 允許從 ORM 物件讀取
        json_encoders={
            uuid.UUID: str     # 👈 告訴 Pydantic：看到 UUID 就轉成 str
        }
    )