from fastapi import APIRouter, HTTPException
from app.schemas.ai_schema import LessonPlanRequest, LessonPlanResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/generate-lesson-plan", response_model=LessonPlanResponse)
async def generate_lesson_plan(request: LessonPlanRequest):
    """
    AI 智慧備課助手
    """
    try:
        print(f"🤖 AI 正在備課中: {request.subject} - {request.topic}")
        result = await ai_service.generate_lesson_plan(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 生成失敗: {str(e)}")