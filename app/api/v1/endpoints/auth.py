from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.db.session import get_db
from app.models.user import User, SchoolProfile, TeacherProfile
from app.schemas.auth_schema import UserRegister, Token
from app.core.security import get_password_hash, verify_password, create_access_token

import httpx
import secrets
from app.schemas.auth_schema import OAuthLogin # 記得匯入新 Schema

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    使用者註冊 (區分 Teacher / School)
    """
    # 1. 檢查 Email 是否已被註冊
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="此 Email 已經被註冊過了"
        )

    # 2. 建立 User 主帳號
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(new_user)
    await db.flush() # 先 flush 拿到 new_user.id

    # 3. 根據角色建立對應 Profile
    if user_in.role == 'school':
        if not user_in.school_name:
            raise HTTPException(status_code=400, detail="學校名稱為必填")
        
        profile = SchoolProfile(
            user_id=new_user.id,
            school_name=user_in.school_name,
            city=user_in.city or "Unknown",
            district=user_in.district or "Unknown"
        )
        db.add(profile)

    elif user_in.role == 'teacher':
        if not user_in.full_name:
            raise HTTPException(status_code=400, detail="老師姓名為必填")
            
        profile = TeacherProfile(
            user_id=new_user.id,
            full_name=user_in.full_name
        )
        db.add(profile)
    
    else:
        raise HTTPException(status_code=400, detail="無效的角色類型 (只能是 teacher 或 school)")

    await db.commit()
    await db.refresh(new_user)

    # 4. 註冊成功直接回傳 Token
    access_token = create_access_token(subject=new_user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": new_user.role,
        "user_id": str(new_user.id)
    }

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    使用者登入 (使用 Form Data)
    username 欄位填 Email
    password 欄位填 密碼
    """
    # 1. 找使用者
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # 2. 驗證密碼
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 發 Token
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": str(user.id)
    }

# 👇 新增以下 OAuth 邏輯
@router.post("/oauth", response_model=Token)
async def oauth_login(
    login_data: OAuthLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    第三方登入 (Google / LINE)
    包含開發測試後門：token 填入 'dev_test_token' 即可跳過驗證
    """
    email = None
    name = None

    # ==========================================
    # 🛠️ 開發測試專用後門 (Dev Mock)
    # ==========================================
    if login_data.token == "dev_test_token":
        print("⚠️ [Dev Mode] 偵測到測試 Token，跳過真實驗證，使用模擬數據。")
        email = login_data.email
        name = login_data.name
        if not email:
            raise HTTPException(status_code=400, detail="測試模式下，請在 Request Body 填寫 email")

    # ==========================================
    # 🌍 真實環境驗證邏輯 (Production)
    # ==========================================
    else:
        async with httpx.AsyncClient() as client:
            # === Google 驗證 ===
            if login_data.provider == 'google':
                verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={login_data.token}"
                response = await client.get(verify_url)
                
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Google Token 無效")
                
                google_info = response.json()
                email = google_info.get('email')
                name = google_info.get('name')

            # === LINE 驗證 ===
            elif login_data.provider == 'line':
                verify_url = "https://api.line.me/oauth2/v2.1/verify"
                response = await client.get(verify_url, params={"access_token": login_data.token})
                
                if response.status_code != 200:
                    raise HTTPException(status_code=400, detail="LINE Token 無效")
                
                # LINE 取得 Profile
                try:
                    profile_res = await client.get(
                        "https://api.line.me/v2/profile",
                        headers={"Authorization": f"Bearer {login_data.token}"}
                    )
                    if profile_res.status_code == 200:
                        line_profile = profile_res.json()
                        name = line_profile.get('displayName')
                        # 如果 LINE 沒給 email，就優先用前端傳來的，不然就偽造一個
                        email = login_data.email or f"{line_profile.get('userId')}@line.user"
                except:
                    pass

    # -----------------------------
    # 共用邏輯：檢查 Email 是否為空
    # -----------------------------
    if not email:
        raise HTTPException(status_code=400, detail="無法取得 Email 資訊")

    # -----------------------------
    # 2. 檢查資料庫 (自動註冊邏輯)
    # -----------------------------
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 如果使用者不存在 -> 自動註冊
    if not user:
        if not login_data.role:
            raise HTTPException(
                status_code=400, 
                detail="NEW_USER_REQUIRED_ROLE"
            )
        
        random_password = secrets.token_urlsafe(16)
        
        new_user = User(
            email=email,
            hashed_password=get_password_hash(random_password),
            role=login_data.role
        )
        db.add(new_user)
        await db.flush()

        if login_data.role == 'teacher':
            profile = TeacherProfile(
                user_id=new_user.id,
                full_name=name or "新老師"
            )
            db.add(profile)
        elif login_data.role == 'school':
            profile = SchoolProfile(
                user_id=new_user.id,
                school_name=name or "新學校",
                city="Unknown",
                district="Unknown"
            )
            db.add(profile)
            
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    # -----------------------------
    # 3. 發放 Token
    # -----------------------------
    access_token = create_access_token(subject=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": str(user.id)
    }