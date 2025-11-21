# app/models/lesson.py
import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class LessonPlan(Base):
    """
    AI 智慧教案表
    """
    __tablename__ = "lesson_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    # 快速索引
    subject: Mapped[str] = mapped_column(String(50))
    grade: Mapped[str] = mapped_column(String(20))
    topic: Mapped[str] = mapped_column(String(100))
    
    # 核心內容：AI 生成的 JSON 結構
    # { "title": "...", "sections": [...], "materials": [...] }
    content: Mapped[Dict[str, Any]] = mapped_column(JSONB)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)