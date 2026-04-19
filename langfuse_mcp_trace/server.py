from mcp.server.fastmcp import FastMCP, Context
from langfuse import Langfuse
import time

mcp = FastMCP("Fab_Equipment_Server")
langfuse = Langfuse()

@mcp.tool()
def get_machine_status(machine_id: str, ctx: Context) -> str:
    """查詢特定機台的當前狀態"""
    
    # -------------------------------------------------------------
    # 關鍵點 1：透過 FastMCP 的 Context 取得請求層的 meta
    # MCP 協議中對應的是 JSON-RPC 的 `_meta` 欄位
    # -------------------------------------------------------------
    request_meta = {}
    if ctx and ctx.request_context and ctx.request_context.meta:
        request_meta = ctx.request_context.meta

    trace_id = request_meta.get("langfuse_trace_id")
    parent_id = request_meta.get("langfuse_parent_id")

    # -------------------------------------------------------------
    # 關鍵點 2：動態判斷是否需要建立 Langfuse Span
    # -------------------------------------------------------------
    if trace_id and parent_id:
        print(f"[Server] 成功攔截 Meta! Trace: {trace_id}, Parent: {parent_id}")
        span = langfuse.span(
            trace_id=trace_id,
            parent_observation_id=parent_id,
            name="mcp_tool:get_machine_status",
            input={"machine_id": machine_id} # 只記錄乾淨的業務參數
        )
        
        try:
            result = _mock_db_query(machine_id)
            span.end(output={"result": result}, level="DEFAULT")
            return result
        except Exception as e:
            span.end(level="ERROR", status_message=str(e))
            raise e
        finally:
            langfuse.flush()
    else:
        # 降級模式：如果 Host 沒有傳 Meta，就當作普通呼叫
        print("[Server] 未收到追蹤 Meta，執行無追蹤模式")
        return _mock_db_query(machine_id)

def _mock_db_query(machine_id: str) -> str:
    time.sleep(0.5) 
    return f"狀態報告：{machine_id} 運作正常"

if __name__ == "__main__":
    mcp.run()