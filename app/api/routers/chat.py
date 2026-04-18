import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.core.agent import agent_reasoning_process

router = APIRouter()

@router.get("/chat/stream")
async def stream_agent_response(query: str):
    """
    建立串流 API 路由，將 Agent 的思考過程與結果轉為 Server-Sent Events (SSE) 格式回傳給前端
    """
    async def event_generator():
        try:
            # 迭代 core/agent 中定義的 agent_reasoning_process 產生器
            async for event_data in agent_reasoning_process(query):
                # 將 Dict 轉換為 JSON 字串，並依照 SSE 格式送出
                payload = json.dumps(event_data, ensure_ascii=False)
                yield f"data: {payload}\n\n"
        except Exception as e:
            # 處理異常，即時通知前端
            error_payload = json.dumps({"event": "error", "data": str(e)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

    # 回傳 StreamingResponse，宣告 SSE 串流
    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream"
    )
