import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector  # 匯入 Vector 型別
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False) # 'teacher', 'school'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 關聯 (1:1)
    school_profile: Mapped["SchoolProfile"] = relationship("SchoolProfile", back_populates="user", uselist=False)
    teacher_profile: Mapped["TeacherProfile"] = relationship("TeacherProfile", back_populates="user", uselist=False)
    
    # 用於反向查詢老師的所有應徵紀錄
    applications = relationship("Application", back_populates="teacher")


class SchoolProfile(Base):
    __tablename__ = "school_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    school_name: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(50))
    district: Mapped[str] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    contact_person: Mapped[Optional[str]] = mapped_column(String(50))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    user: Mapped["User"] = relationship("User", back_populates="school_profile")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50))
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    
    # JSONB 欄位：儲存專業類科 CheckBox、教學風格等
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    
    # JSONB 欄位：履歷詳細內容
    resume_data: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})

    # [AI] Gemini Embedding (768維)
    intro_embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768))

    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")