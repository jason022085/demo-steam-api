from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# 載入環境變數
load_dotenv()

# 初始化 FastAPI 應用程式
app = FastAPI(title="Demo Stream API")

# 設定 CORS (跨來源資源共用) 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 預設 port
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有 HTTP 標頭
)

# 匯入 Router
from app.api.routers.chat import router as chat_router

# 將 Router 掛載到應用程式，並設定 prefix (原先路徑為 /api/chat/stream)
app.include_router(chat_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
