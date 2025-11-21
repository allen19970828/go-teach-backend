from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
import uuid

from app.db.session import get_db
from app.models.chat import Message, ChatRoom
from app.schemas.chat_schema import MessageRead
from app.api.v1.endpoints.jobs import get_current_user_id # 借用權限驗證

router = APIRouter()

# app/api/v1/endpoints/chat.py

@router.get("/{room_id}/messages", response_model=List[MessageRead])
async def get_chat_history(
    room_id: str,
    user_id: str = Depends(get_current_user_id), # 👈 這裡會驗證 Token
    db: AsyncSession = Depends(get_db)
):
    # 👇 debug: 印出是誰在查
    print(f"🔍 [Chat] User requesting: {user_id}")
    print(f"🔍 [Chat] Room ID: {room_id}")

    try:
        room_uuid = uuid.UUID(room_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="無效的 Room ID")

    result = await db.execute(select(ChatRoom).where(ChatRoom.id == room_uuid))
    room = result.scalar_one_or_none()
    
    if not room:
        # 👇 debug: 印出找不到
        print("❌ 找不到房間")
        raise HTTPException(status_code=404, detail="找不到此聊天室")

    query = select(Message).where(Message.chat_room_id == room_uuid).order_by(Message.created_at.asc())
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # 👇 debug: 印出找到幾則
    print(f"✅ 找到 {len(messages)} 則訊息")
    
    return [
        MessageRead(
            id=msg.id,
            sender_id=str(msg.sender_id), # 強制轉字串
            content=msg.content,
            created_at=msg.created_at
        ) 
        for msg in messages
    ]