import asyncio
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 透過 Pydantic 定義輸入 Schema，讓 LLM 清楚知道應該傳入什麼格式的參數
class GraphQueryInput(BaseModel):
    query: str = Field(..., description="具體的搜尋條件，例如：'尋找 M_EUV_001 的 Kshift 關聯'")

@tool("Knowledge_Graph", args_schema=GraphQueryInput)
async def Knowledge_Graph(query: str) -> str:
    """尋找機台與光罩關聯的知識圖譜。"""
    try:
        await asyncio.sleep(1.5) # 模擬真實資料庫查詢耗時
        return f"找到 3 筆歷史 Case 共享同一批光罩 (查詢條件: {query})"
    except Exception as e:
        return f"系統查詢知識圖譜時發生錯誤: {str(e)}，請調整查詢條件後再試。"

class RAGQueryInput(BaseModel):
    query: str = Field(..., description="檔案或報告的搜尋條件，例如：'提取這 3 筆 Case 的處理紀錄'")

@tool("RAG_Retrieval", args_schema=RAGQueryInput)
async def RAG_Retrieval(query: str) -> str:
    """提取關聯 Case 的處理紀錄與 SOP 報告。"""
    try:
        await asyncio.sleep(1) # 模擬向量資料庫搜尋耗時
        return f"成功提取 3 份 SOP 報告 (查詢條件: {query})"
    except Exception as e:
        return f"系統查詢 RAG 時發生錯誤: {str(e)}，請提醒使用者提供更多資訊。"