# app/models/job.py
import uuid
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Text, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text) # AI 生成的職缺內文
    
    # 篩選欄位
    city: Mapped[str] = mapped_column(String(50))

    district: Mapped[str] = mapped_column(String(50)) 

    edu_stage: Mapped[str] = mapped_column(String(20))
    subject: Mapped[str] = mapped_column(String(50))
    
    salary_type: Mapped[Optional[str]] = mapped_column(String(20))
    salary_amount: Mapped[Optional[int]] = mapped_column(Integer)
    
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # [AI] 職缺 Embedding (768維)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768))

    # 👇 新增這行關聯 用於反向查詢職缺的所有應徵紀錄
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
