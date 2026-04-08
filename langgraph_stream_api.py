import json
import asyncio
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from langchain_core.messages import HumanMessage

# 載入環境變數 (確保有 .env 檔案包含 OPENAI_API_KEY)
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 定義真正的 LangChain 工具
@tool
async def Knowledge_Graph(query: str) -> str:
    """尋找機台與光罩關聯的知識圖譜。輸入必須是具體的搜尋條件，例如：'尋找 M_EUV_001 的 Kshift 關聯'"""
    await asyncio.sleep(1.5) # 模擬真實資料庫查詢耗時
    return f"找到 3 筆歷史 Case 共享同一批光罩 (查詢條件: {query})"

@tool
async def RAG_Retrieval(query: str) -> str:
    """提取關聯 Case 的處理紀錄與 SOP 報告。輸入必須是檔案或報告的搜尋條件，例如：'提取這 3 筆 Case 的處理紀錄'"""
    await asyncio.sleep(1) # 模擬向量資料庫搜尋耗時
    return f"成功提取 3 份 SOP 報告 (查詢條件: {query})"

# 2. 建立 LangGraph Agent
tools = [Knowledge_Graph, RAG_Retrieval]

# 初始化 LLM 模型，此處以 o3-mini 為例 (預設開啟 streaming)
# 若沒有設定 OPENAI_API_KEY，將會在啟動伺服器或調用 API 時報錯
llm = ChatOpenAI(model="o3-mini", reasoning_effort="high", streaming=True)

# 使用 langgraph.prebuilt 建立 ReAct 架構的 Agent
agent_executor = create_react_agent(llm, tools)

async def agent_reasoning_process(query: str):
    """
    透過 LangGraph astream_events 捕獲真實的 Agent 思考與工具調用過程
    """
    yield {"event": "status", "data": "🧠 正在解析問題意圖 (LangGraph)..."}
    
    # 傳入使用者的問題
    inputs = {"messages": [HumanMessage(content=f"使用者問題: {query}\n請在需要時使用知識圖譜與RAG工具來輔助回答。")]}
    
    try:
        # 使用 astream_events (version="v2") 串流事件
        async for event in agent_executor.astream_events(inputs, version="v2"):
            kind = event["event"]
            name = event.get("name", "")
            data = event.get("data", {})
            
            if kind == "on_chat_model_stream":
                # 捕獲 LLM 的文字串流
                chunk = data.get("chunk")
                # 只有當 chunk 包含實際回覆內容（且不是 tool_calls token）時才拋出
                if chunk and chunk.content:
                    yield {"event": "content_chunk", "data": chunk.content}
                    
            elif kind == "on_tool_start":
                # 捕獲工具調用開始
                input_data = data.get("input", {})
                # 避免傳送非工具的串流，這裡只攔截自定義的這兩個工具
                if name in ["Knowledge_Graph", "RAG_Retrieval"]:
                    yield {
                        "event": "tool_start", 
                        "data": {
                            "tool": name, 
                            "input": str(input_data)
                        }
                    }
                
            elif kind == "on_tool_end":
                # 捕獲工具調用結束
                output_data = data.get("output", "")
                if name in ["Knowledge_Graph", "RAG_Retrieval"]:
                    yield {
                        "event": "tool_end", 
                        "data": {
                            "tool": name, 
                            "result": str(output_data.content if hasattr(output_data, "content") else output_data)
                        }
                    }
                
    except Exception as e:
        yield {"event": "error", "data": f"LangGraph 執行發生錯誤: {str(e)}"}

@app.get("/api/chat/stream")
async def stream_agent_response(query: str):
    async def event_generator():
        try:
            async for event_data in agent_reasoning_process(query):
                # 將 Dict 轉換為 JSON 字串，並依照 SSE 格式 (data: {...}\n\n) 送出
                payload = json.dumps(event_data, ensure_ascii=False)
                yield f"data: {payload}\n\n"
        except Exception as e:
            # 處理中途斷線或異常，即時通知前端
            error_payload = json.dumps({"event": "error", "data": str(e)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream" # 宣告這是 SSE 串流
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)