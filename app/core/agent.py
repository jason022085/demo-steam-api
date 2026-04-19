import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langfuse.langchain import CallbackHandler
from langchain_core.callbacks import CallbackManagerForToolRun
from app.tools.registry import get_agent_skills

# 1. 取得需要使用的 Tools
tools = get_agent_skills(categories=["knowledge", "finance", "meta"])

# 2. 初始化 LLM
llm = ChatOpenAI(model="o3-mini", reasoning_effort="high", streaming=True)
llm_with_tools = llm.bind_tools(tools)

# 3. 定義 LangGraph 狀態圖節點與邊
async def call_model(state: MessagesState):
    messages = state["messages"]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 建立與編譯 Workflow
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

agent_executor = workflow.compile()

from typing import Optional

# 4. 定義 Agent 執行與串流事件解析邏輯
async def agent_reasoning_process(query: str, session_id: Optional[str] = None, user_id: Optional[str] = None):
    """
    透過 LangGraph astream 捕獲 Agent 的步驟執行結果，
    並將過程中的狀態、工具調用、內容片段以產生器 (Generator) 方式 yield 出來
    """
    yield {"event": "status", "data": "🧠 正在解析問題意圖 (LangGraph)..."}
    
    inputs = {
        "messages": [
            HumanMessage(
                content=f"使用者問題: {query}\n請根據使用者需求，主動使用合適的工具。若需要了解有哪些工具或不清楚如何使用，可先透過 Discover_Skills 尋找 SKILL.md 文件，並使用 Read_Skill_Doc 讀取文件內容以學習技能的使用方式。"
            )
        ]
    }
    
    try:
        langfuse_handler = CallbackHandler()
        
        # 在 LangChain/LangGraph v3+ 版本中，session_id 和 user_id 需要透過 metadata 傳遞
        run_metadata = {}
        if session_id:
            run_metadata["langfuse_session_id"] = session_id
        if user_id:
            run_metadata["langfuse_user_id"] = user_id

        async for msg_chunk, metadata in agent_executor.astream(
            inputs, 
            stream_mode="messages",
            config={
                "callbacks": [langfuse_handler],
                "metadata": run_metadata
            }
        ):
            node = metadata.get("langgraph_node")
            
            if node == "agent":
                if msg_chunk.content:
                    yield {"event": "content_chunk", "data": msg_chunk.content}
                
                if hasattr(msg_chunk, "tool_call_chunks") and msg_chunk.tool_call_chunks:
                    for tc in msg_chunk.tool_call_chunks:
                        if tc.get("name"):
                            yield {
                                "event": "tool_start", 
                                "data": {
                                    "tool": tc["name"], 
                                    "input": "開始調用工具..."
                                }
                            }
                            
            elif node == "tools":
                if msg_chunk.content:
                    yield {
                        "event": "tool_end", 
                        "data": {
                            "tool": msg_chunk.name, 
                            "result": str(msg_chunk.content)
                        }
                    }
                
    except Exception as e:
        yield {"event": "error", "data": f"LangGraph 執行發生錯誤: {str(e)}"}
