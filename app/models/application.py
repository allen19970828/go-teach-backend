import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 關聯外鍵
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    # 應徵狀態：pending (待處理), contacting (聯絡中), accepted (錄取), rejected (婉拒)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 建立關聯 (方便查詢)
    job = relationship("Job", back_populates="applications")
    teacher = relationship("User", back_populates="applications")