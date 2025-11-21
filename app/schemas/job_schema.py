from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# 職缺基本資料 (共用)
class JobBase(BaseModel):
    title: str
    description: str
    city: str
    district: str
    edu_stage: str  # elementary, junior...
    subject: str
    
    salary_type: str # daily, session
    salary_amount: int
    start_date: date
    end_date: date

# 建立職缺時的請求
class JobCreate(JobBase):
    pass

# 回傳給前端的職缺卡片
class JobCard(JobBase):
    id: str
    school_name: str  # 這是關聯查出來的
    school_id: str
    is_active: bool
    created_at: date

    class Config:
        from_attributes = True