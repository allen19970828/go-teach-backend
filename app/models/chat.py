import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 聊天室綁定關係 (針對某個職缺，某個老師與學校的對話)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    school_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 關聯訊息
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # 使用自增整數確保順序
    
    chat_room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_rooms.id"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) # 誰傳的
    
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    room = relationship("ChatRoom", back_populates="messages")