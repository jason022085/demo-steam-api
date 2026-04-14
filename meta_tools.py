import os
import glob
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import asyncio

class DiscoverSkillsInput(BaseModel):
    query: str = Field(..., description="你想尋找什麼類型的技能？(例如：'財報', '知識庫')")

@tool("Discover_Skills", args_schema=DiscoverSkillsInput)
async def Discover_Skills(query: str) -> str:
    """搜尋系統中有哪些可用的 SKILL.md (技能說明) 文件。回傳檔案列表。"""
    try:
        await asyncio.sleep(0.5)
        # 在這裡我們簡單列出當前目錄與子目錄下所有的 .md 檔案（或者明確篩選 skill.md）
        # 實務上可以做更複雜的語意搜尋，這裡做簡單的檔名與路徑比對
        md_files = glob.glob("**/*.md", recursive=True)
        
        # 過濾掉 README.md 等無關檔案，專注於 skill 相關文件
        skill_docs = [f for f in md_files if "skill" in f.lower()]
        
        if not skill_docs:
            return "目前系統中沒有找到任何與 Skill 相關的 md 文件。"
            
        return f"找到以下 Skill 說明文件：\n" + "\n".join(skill_docs) + "\n\n(提示: 你可以使用 Read_Skill_Doc 工具來讀取這些檔案的詳細內容)"
    except Exception as e:
        return f"尋找 Skill 文件時發生錯誤: {str(e)}"

class ReadSkillDocInput(BaseModel):
    file_path: str = Field(..., description="要讀取的 SKILL.md 檔案路徑，例如：'skill.md'")

@tool("Read_Skill_Doc", args_schema=ReadSkillDocInput)
async def Read_Skill_Doc(file_path: str) -> str:
    """讀取指定的 SKILL.md 文件內容，以了解該技能的詳細使用方式與參數。"""
    try:
        if not os.path.exists(file_path):
            return f"找不到檔案: {file_path}"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"--- {file_path} 的內容 ---\n{content}\n---"
    except Exception as e:
        return f"讀取文件時發生錯誤: {str(e)}"