from app.schemas.application_schema import ApplicationCreate, ApplicantCard

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import List, Optional

from app.db.session import get_db
from app.models.job import Job
from app.models.user import User, SchoolProfile, TeacherProfile
from app.models.application import Application
from app.schemas.job_schema import JobCreate, JobCard
from app.core.security import verify_password # 這裡暫時用不到，但可以留著
from app.api.v1.endpoints.auth import router as auth_router # 這裡需要一個取得當前用戶的依賴

# 👇 我們需要先寫一個簡單的 dependency 來取得當前登入的使用者
# (正式專案會寫在 app/api/deps.py，這裡先簡化處理)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 

from jose import jwt, JWTError # 記得確認有 import JWTError
# from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.services.ai_service import ai_service

router = APIRouter()

security = HTTPBearer()


async def get_current_user_id(
    token_obj: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    解析 Token 取得 User ID (支援直接貼上 Token)
    """
    token = token_obj.credentials # 從 header 拿出字串
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="無效的憑證: 找不到 User ID")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="憑證已過期或無效")

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
#     """解析 Token 取得 User ID"""
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="無效的憑證")
#         return user_id
#     except Exception:
#         raise HTTPException(status_code=401, detail="憑證已過期或無效")

# ==========================================
# API 實作
# ==========================================

@router.post("/", response_model=JobCard)
async def create_job(
    job_in: JobCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    刊登新職缺 (限學校)
    會自動進行 AI Embedding 處理
    """
    # 1. 確認使用者是學校
    # (這裡省略了查 User role 的步驟，直接假設前端邏輯正確，或是之後補上 Role Check)
    
    # 2. 呼叫 AI 計算向量 (非同步)
    # 將 標題 + 科目 + 描述 組合起來做向量化，搜尋會更準
    text_for_embedding = f"{job_in.title} {job_in.subject} {job_in.description}"
    vector = await ai_service.get_embedding(text_for_embedding)

    # 3. 建立職缺
    new_job = Job(
        school_id=user_id,
        title=job_in.title,
        description=job_in.description,
        city=job_in.city,
        district=job_in.district,
        edu_stage=job_in.edu_stage,
        subject=job_in.subject,
        salary_type=job_in.salary_type,
        salary_amount=job_in.salary_amount,
        start_date=job_in.start_date,
        end_date=job_in.end_date,
        embedding=vector # 存入向量
    )
    
    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # 4. 補上學校名稱 (回傳給前端顯示用)
    # 為了效能，這裡簡單再查一次 Profile
    res = await db.execute(select(SchoolProfile).where(SchoolProfile.user_id == user_id))
    profile = res.scalar_one_or_none()
    
    # 手動組裝 Response (因為 Pydantic 有時候沒辦法直接從 DB model 轉 school_name)
    return JobCard(
        id=str(new_job.id),
        school_name=profile.school_name if profile else "未知學校",
        school_id=str(new_job.school_id),
        is_active=new_job.is_active,
        created_at=new_job.created_at.date(),
        **job_in.model_dump()
    )

@router.get("/", response_model=List[JobCard])
async def get_jobs(
    keyword: Optional[str] = None,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    職缺搜尋列表 (支援 AI 語意搜尋)
    """
    query = select(Job, SchoolProfile).join(SchoolProfile, Job.school_id == SchoolProfile.user_id)
    
    # 條件篩選
    if city:
        query = query.where(Job.city == city)

    # 關鍵字搜尋 (如果有關鍵字，走 Vector Search；沒有則依時間排序)
    if keyword:
        print(f"🔍 啟動 AI 語意搜尋: {keyword}")
        # 1. 將關鍵字轉向量
        query_vector = await ai_service.get_embedding(keyword)
        
        # 2. 使用 pgvector 的 L2 距離排序 (越小越近)
        query = query.order_by(Job.embedding.l2_distance(query_vector))
    else:
        # 預設：照建立時間新到舊
        query = query.order_by(desc(Job.created_at))

    result = await db.execute(query)
    rows = result.all() # 格式是 [(Job, SchoolProfile), ...]

    # 組裝結果
    job_list = []
    for job, profile in rows:
        job_card = JobCard(
            id=str(job.id),
            school_name=profile.school_name,
            school_id=str(job.school_id),
            is_active=job.is_active,
            created_at=job.created_at.date(),
            title=job.title,
            description=job.description,
            city=job.city,
            district=job.district,
            edu_stage=job.edu_stage,
            subject=job.subject,
            salary_type=job.salary_type,
            salary_amount=job.salary_amount,
            start_date=job.start_date,
            end_date=job.end_date
        )
        job_list.append(job_card)

    return job_list

@router.post("/{job_id}/apply")
async def apply_job(
    job_id: str,
    apply_in: ApplicationCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    [老師] 應徵職缺
    """
    # 1. 確認是老師身份
    res = await db.execute(select(TeacherProfile).where(TeacherProfile.user_id == user_id))
    teacher_profile = res.scalar_one_or_none()
    
    if not teacher_profile:
        raise HTTPException(status_code=403, detail="只有老師可以應徵職缺")

    # 2. 檢查職缺是否存在
    res = await db.execute(select(Job).where(Job.id == job_id))
    job = res.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="職缺不存在")

    # 3. 檢查是否重複應徵
    res = await db.execute(
        select(Application).where(
            and_(Application.job_id == job_id, Application.teacher_id == user_id)
        )
    )
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="您已經應徵過此職缺")

    # 4. 建立應徵紀錄
    application = Application(
        job_id=job_id,
        teacher_id=user_id,
        cover_letter=apply_in.cover_letter
    )
    db.add(application)
    await db.commit()
    
    return {"message": "應徵成功", "application_id": str(application.id)}


@router.get("/{job_id}/applicants", response_model=List[ApplicantCard])
async def get_job_applicants(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    [學校] 查看某職缺的應徵者
    """
    # 1. 檢查職缺是否屬於該學校
    res = await db.execute(select(Job).where(and_(Job.id == job_id, Job.school_id == user_id)))
    job = res.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=403, detail="您無權查看此職缺，或職缺不存在")

    # 2. 查詢所有應徵者 (Join Application + TeacherProfile)
    query = (
        select(Application, TeacherProfile)
        .join(TeacherProfile, Application.teacher_id == TeacherProfile.user_id)
        .where(Application.job_id == job_id)
        .order_by(desc(Application.applied_at))
    )
    
    res = await db.execute(query)
    rows = res.all()

    # 3. 組裝回傳資料
    results = []
    for app, profile in rows:
        results.append(ApplicantCard(
            application_id=str(app.id),
            teacher_id=str(app.teacher_id),
            teacher_name=profile.full_name,
            status=app.status,
            cover_letter=app.cover_letter,
            applied_at=app.applied_at
        ))
        
    return results