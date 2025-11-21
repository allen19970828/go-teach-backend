import google.generativeai as genai
import json
from app.core.config import settings

# 設定 API Key
genai.configure(api_key=settings.GOOGLE_API_KEY)

class AIService:
    def __init__(self):
        # 1. 強制使用最穩定的 gemini-1.5-flash
        # 避免使用 exp 版本，因為額度不穩定
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )

    async def generate_lesson_plan(self, req) -> dict:
        """
        生成教案 (含自動 Mock 機制)
        """
        prompt = f"""
        你是一位專業的台灣中小學資深教師。請為一位「代課老師」設計一份教案。
        
        [課程資訊]
        - 科目: {req.subject}
        - 年級: {req.grade}
        - 單元: {req.topic}
        - 時間: {req.duration} 分鐘
        
        [輸出 JSON 格式]
        {{
            "title": "標題",
            "materials_needed": ["材料1"],
            "sections": [
                {{ "phase": "引起動機", "time_allocation": "5 min", "activity": "..." }},
                {{ "phase": "發展活動", "time_allocation": "...", "activity": "..." }},
                {{ "phase": "綜合活動", "time_allocation": "...", "activity": "..." }}
            ],
            "memo": "備註"
        }}
        """

        try:
            print(f"🚀 [AI Service] 正在呼叫 Google Gemini (1.5-flash): {req.topic}...")
            
            # 嘗試呼叫真 AI
            response = await self.model.generate_content_async(prompt)
            
            # 嘗試解析 JSON
            result = json.loads(response.text)
            print("✅ AI 成功回應！")
            return result

        except Exception as e:
            # =================================================
            # 🚨 這裡就是你的救生圈！
            # 只要發生任何錯誤 (429額度滿, 網路斷線, 模型找不到...)
            # 程式會進入這裡，回傳假資料，保證 API 不會掛掉
            # =================================================
            print(f"⚠️ AI 呼叫失敗 (可能是額度滿了): {e}")
            print("🔄 啟動 Fallback 模式：回傳測試資料。")
            
            return {
                "title": f"[測試模式] {req.subject}: {req.topic}",
                "materials_needed": ["課本", "學習單", "投影機 (測試用)", "平板電腦"],
                "sections": [
                    {
                        "phase": "引起動機 (Mock)",
                        "time_allocation": "5 min",
                        "activity": "⚠️ Google API 額度冷卻中，這是自動產生的測試內容。請想像這裡有一段很棒的開場影片。"
                    },
                    {
                        "phase": "發展活動 (Mock)",
                        "time_allocation": f"{req.duration - 10} min",
                        "activity": f"老師講解 {req.topic} 的重點。學生分組進行討論與實作。這是測試文字，用來驗證前端排版是否正常。"
                    },
                    {
                        "phase": "綜合活動 (Mock)",
                        "time_allocation": "5 min",
                        "activity": "總結課程重點，並請學生完成線上測驗。"
                    }
                ],
                "memo": "💡 提示：這是 Mock 資料。請稍後再試，或更換 API Key 以取得真實 AI 回應。"
            }
        

    # ...原本的 import 和 init ...

    # 👇 新增這個方法在 AIService class 裡面
    async def get_embedding(self, text: str) -> list[float]:
        """
        將文字轉換為向量 (使用 text-embedding-004)
        """
        try:
            # 清理文字 (移除換行符號等，避免影響向量品質)
            clean_text = text.replace("\n", " ")
            
            # 呼叫 Google Embedding API
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=clean_text,
                task_type="retrieval_document"
            )
            return result['embedding']
            
        except Exception as e:
            print(f"⚠️ Embedding 失敗: {e}")
            # Fallback: 如果失敗，回傳一個全 0 的向量 (768維)，避免程式崩潰
            return [0.0] * 768

ai_service = AIService()
