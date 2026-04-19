from langchain_core.tools import tool
from langchain_core.callbacks import CallbackManagerForToolRun

# 假設這是您客製化支援 meta 的 MCP Client Wrapper
class EnhancedMCPClient:
    def call_tool(self, name: str, arguments: dict, meta: dict = None):
        print(f"[Host Client] 送出請求 -> Args: {arguments}, Meta: {meta}")
        # 底層實作會將 meta 打包進 MCP JSON-RPC 的 `params._meta` 中
        return "SUCCESS"

mcp_client = EnhancedMCPClient()

@tool
def get_machine_status_via_mcp(machine_id: str, run_manager: CallbackManagerForToolRun = None) -> str:
    """呼叫 MCP Server 查詢機台狀態"""
    
    # 從 LangChain 內部機制提取 ID
    span_id = str(run_manager.run_id)
    trace_id = run_manager.metadata.get("langfuse_trace_id")
    if not trace_id:
        trace_id = str(run_manager.parent_run_id)

    # 封裝要傳給 MCP 協議層的 Meta
    tracing_meta = {
        "langfuse_trace_id": trace_id,
        "langfuse_parent_id": span_id
    }

    # 業務邏輯參數 (純淨無污染)
    tool_arguments = {
        "machine_id": machine_id
    }

    # 呼叫支援傳遞 Meta 的 Client 方法
    return mcp_client.call_tool(
        name="get_machine_status",
        arguments=tool_arguments,
        meta=tracing_meta 
    )