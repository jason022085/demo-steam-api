import asyncio
from langchain_core.tools import tool
from pydantic import BaseModel, Field

class FinancialReportInput(BaseModel):
    company_symbol: str = Field(..., description="公司股票代號，例如：'AAPL', 'TSM'")
    year: int = Field(..., description="財報年份，例如：2023")

@tool("Analyze_Financial_Report", args_schema=FinancialReportInput)
async def Analyze_Financial_Report(company_symbol: str, year: int) -> str:
    """分析公司的年度財報，提供營收、淨利與毛利率等關鍵指標。"""
    try:
        await asyncio.sleep(1.5) # 模擬查詢或分析耗時
        return f"【{year} 年度財報分析】{company_symbol} 展現了穩健的營運體質。今年度營收較去年顯著成長，毛利率維持在業界高標水準（約 50% 以上），淨利表現優於市場預期，顯示其在成本控管與產品定價上具有優勢。"
    except Exception as e:
        return f"財報分析發生錯誤: {str(e)}，請確認公司代號或年份是否正確。"
