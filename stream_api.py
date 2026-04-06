import json
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 設定允許跨網域連線
app.add_middleware(
    CORSMiddleware,
    # 把 localhost 和 127.0.0.1 都加進去，確保萬無一失
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def agent_reasoning_process(query: str):
    """
    模擬 Agent 的執行與思考過程 (實際開發中，這裡會替換為 LangGraph 的 astream_events)
    """
    # 1. 思考階段
    yield {"event": "status", "data": "🧠 正在解析問題意圖..."}
    await asyncio.sleep(1) # 模擬思考耗時
    
    # 2. 調用圖譜工具
    yield {"event": "tool_start", "data": {"tool": "Knowledge_Graph", "input": "尋找 M_EUV_001 的 Kshift 關聯"}}
    await asyncio.sleep(1.5) # 模擬資料庫查詢耗時
    yield {"event": "tool_end", "data": {"tool": "Knowledge_Graph", "result": "找到 3 筆歷史 Case 共享同一批光罩"}}
    
    # 3. 調用 RAG 工具
    yield {"event": "tool_start", "data": {"tool": "RAG_Retrieval", "input": "提取這 3 筆 Case 的處理紀錄"}}
    await asyncio.sleep(1)
    yield {"event": "tool_end", "data": {"tool": "RAG_Retrieval", "result": "成功提取 3 份 SOP 報告"}}
    
    # 4. 生成最終回覆 (Token 串流)
    yield {"event": "status", "data": "✍️ 正在總結報告..."}
    final_answer = "根據知識圖譜與歷史紀錄的比對，這台機台的異常高機率與光罩老化有關..."
    for char in final_answer:
        yield {"event": "content_chunk", "data": char}
        await asyncio.sleep(0.05) # 模擬 LLM token 生成

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