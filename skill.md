# 財報分析 (Financial Analysis Skill)

這個 Skill 模組提供代理程式 (Agent) 進行企業財務報表分析的能力。它被設計為一個 LangChain 工具，可以供模型在決策和推理時呼叫。

## 包含的工具 (Tools)

### `Analyze_Financial_Report`

- **功能**：分析指定公司與年份的年度財報，提供營收、淨利與毛利率等關鍵指標的摘要分析。
- **輸入參數**：
  - `company_symbol` (字串): 公司股票代號。例如：`'AAPL'` 或 `'TSM'`。
  - `year` (整數): 要查詢的財報年份。例如：`2023`。
- **回傳值** (字串)：一段整合了該公司當年度營運狀況的分析報告。

## 使用方式

我們已經將財報分析的工具註冊至 `registry.py` 中的 `finance` 類別內。若要在你的 LangGraph Agent 流程中使用它，請在取得工具清單時引入對應的類別：

```python
from registry import get_agent_skills

# 取得包含知識圖譜與財報分析的 Tools
tools = get_agent_skills(categories=["knowledge", "finance"])
```

## 擴充指南

如果未來需要串接真實的財報 API (例如 Alpha Vantage, Yahoo Finance, 或公開資訊觀測站)，請直接修改 `financial.py` 中的 `Analyze_Financial_Report` 函式：
1. 將原本的模擬延遲 (`await asyncio.sleep`) 替換為實際的 HTTP 請求 (如 `httpx` 或 `aiohttp`)。
2. 爬取或解析回傳的 JSON 結構，並整理為 Agent 容易閱讀的文字格式。
