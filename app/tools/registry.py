from typing import List

# 引入各個領域的 Skills
from app.tools.knowledge import Knowledge_Graph, RAG_Retrieval
from app.tools.financial import Analyze_Financial_Report
from app.tools.meta_tools import Discover_Skills, Read_Skill_Doc

# 建立一個全域的工具註冊表，按照業務領域進行分類
AVAILABLE_SKILLS = {
    "knowledge": [Knowledge_Graph, RAG_Retrieval],
    "finance": [Analyze_Financial_Report],
    "meta": [Discover_Skills, Read_Skill_Doc],
    # 未來你可以輕鬆擴充其他類型的 Skills，例如：
    # "database": [Query_Database_Tool, Check_Status_Tool],
    # "api": [Call_External_Service_Tool]
}

def get_agent_skills(categories: List[str] = None) -> list:
    """
    根據傳入的類別清單，動態回傳該 Agent 允許使用的 Skills 陣列。
    如果不指定，預設回傳基礎知識工具。
    """
    if categories is None:
        categories = ["knowledge"]
        
    skills = []
    for category in categories:
        if category in AVAILABLE_SKILLS:
            skills.extend(AVAILABLE_SKILLS[category])
    return skills