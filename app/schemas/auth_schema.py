from pydantic import BaseModel, EmailStr
from typing import Optional
from typing import Literal

# 註冊請求
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str  # 'teacher' 或 'school'
    
    # 學校專用欄位
    school_name: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    
    # 老師專用欄位
    full_name: Optional[str] = None

# 登入成功後回傳的 Token
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str


class OAuthLogin(BaseModel):
    provider: Literal['google', 'line']  # 限制只能填 google 或 line
    token: str                           # 前端拿到的 access_token 或 id_token
    role: Optional[str] = None           # 如果是新用戶，必須傳入角色 (teacher/school)
    
    # 選填：如果前端能拿到這些基本資料，直接傳過來可以省去後端解析的工
    email: Optional[EmailStr] = None     
    name: Optional[str] = None
