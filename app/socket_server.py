import socketio
from jose import jwt
from urllib.parse import parse_qs
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.chat import Message, ChatRoom
from app.models.user import User
from sqlalchemy import select
from datetime import datetime

# 建立 Socket.IO Server (非同步模式)
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=['*'] # 允許所有來源連線
)

# 建立 ASGI App (讓 FastAPI 可以掛載它)
socket_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    """
    當前端連線時觸發
    在此驗證 Token (前端需將 token 放在 query string: ?token=xxx)
    """
    try:
        query_string = environ.get('QUERY_STRING', '')
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]
        
        if not token:
            return False # 拒絕連線

        # 驗證 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        # 將 user_id 綁定到這個 session (sid)
        async with sio.session(sid) as session:
            session['user_id'] = user_id
            
        print(f"✅ Socket 連線成功: {user_id} (sid: {sid})")
        return True
        
    except Exception as e:
        print(f"❌ Socket 驗證失敗: {e}")
        return False

@sio.event
async def join_room(sid, data):
    """
    事件：使用者加入聊天室
    data: { "room_id": "uuid..." }
    """
    room_id = data.get("room_id")
    if room_id:
        sio.enter_room(sid, room_id)
        print(f"📥 使用者加入房間: {room_id}")

@sio.event
async def send_message(sid, data):
    """
    事件：發送訊息
    data: { "room_id": "...", "content": "..." }
    """
    async with sio.session(sid) as session:
        sender_id = session.get('user_id')

    room_id = data.get("room_id")
    content = data.get("content")

    if not room_id or not content:
        return

    # 1. 存入資料庫
    async with AsyncSessionLocal() as db:
        msg = Message(
            chat_room_id=room_id,
            sender_id=sender_id,
            content=content
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        
        created_at_str = msg.created_at.isoformat()

    # 2. 推播給房間內的所有人 (包含自己)
    # 前端收到這個事件後，把訊息顯示在畫面上
    await sio.emit('receive_message', {
        "id": msg.id,
        "sender_id": sender_id,
        "content": content,
        "created_at": created_at_str
    }, room=room_id)
    
    print(f"💬 訊息已傳送: {content} (Room: {room_id})")