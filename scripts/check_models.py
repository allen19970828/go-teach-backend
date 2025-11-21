# scripts/check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 載入 .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ 找不到 GOOGLE_API_KEY")
    exit()

genai.configure(api_key=api_key)

print("🔍 正在查詢你的 API Key 可用的模型列表...\n")

try:
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 可用: {m.name}")
            available_models.append(m.name)
    
    print("\n" + "-"*30)
    if not available_models:
        print("❌ 你的 API Key似乎沒有任何生成模型的權限，請檢查 Google AI Studio 設定。")
    else:
        print("💡 建議：請將 app/services/ai_service.py 裡的模型名稱換成上面其中一個。")
        print("   (通常去掉 'models/' 前綴即可，例如 'gemini-pro')")

except Exception as e:
    print(f"❌ 查詢失敗: {e}")