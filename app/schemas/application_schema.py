from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 老師應徵時填寫的資料
class ApplicationCreate(BaseModel):
    cover_letter: Optional[str] = None  # 簡單的自我推薦信

# 學校看到的應徵者資料
class ApplicantCard(BaseModel):
    application_id: str
    teacher_id: str
    teacher_name: str
    status: str
    cover_letter: Optional[str]
    applied_at: datetime
    
    # 未來可以補上老師的 email 或電話