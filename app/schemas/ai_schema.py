from pydantic import BaseModel
from typing import List, Optional

# 前端傳過來的參數
class LessonPlanRequest(BaseModel):
    subject: str            # 科目 (e.g. 自然)
    grade: str              # 年級 (e.g. 小學三年級)
    topic: str              # 單元 (e.g. 空氣的流動)
    duration: int = 40      # 時間 (預設 40 分鐘)
    textbook_version: Optional[str] = None  # 版本 (e.g. 康軒)
    student_level: Optional[str] = None     # 學生特質備註

# 回傳給前端的詳細結構
class LessonSection(BaseModel):
    phase: str              # 階段 (引起動機、發展活動...)
    time_allocation: str    # 時間分配
    activity: str           # 活動內容

class LessonPlanResponse(BaseModel):
    title: str
    materials_needed: List[str]
    sections: List[LessonSection]
    memo: str