# tools.py
import os
import requests
from dotenv import load_dotenv
from qa import FinAgentQA
from config import NEWS_API_KEY

load_dotenv()

# init QA engine (singleton)
qa_engine = FinAgentQA(top_k=4)

def search_reports_sync(query: str) -> str:
    """
    Sync wrapper for searching reports; returns a short text answer + sources.
    """
    try:
        answer, sources = qa_engine.query(query)
        srcs = ", ".join(md.get("source", "unknown") for md in sources)
        return f"{answer}\n\nSources: {srcs}"
    except Exception as e:
        return f"SearchReports error: {e}"

def calculate(expression: str) -> str:
    """
    Safe-ish calculation helper. Accepts arithmetic expression like '((120 - 100) / 100) * 100'.
    Note: eval is used with empty builtins to limit risk.
    """
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"

# WebNewsTool using NewsAPI (if key provided)
NEWS_API_URL = "https://newsapi.org/v2/everything"

def web_news(query: str, page_size: int = 5, lang: str = "zh") -> str:
    if not NEWS_API_KEY:
        return "News API key not configured (NEWS_API_KEY missing)."
    params = {"q": query, "apiKey": NEWS_API_KEY, "pageSize": page_size, "language": lang}
    try:
        r = requests.get(NEWS_API_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", [])
        if not articles:
            return "No recent news found for the query."
        lines = []
        for i, a in enumerate(articles):
            title = a.get("title", "No title")
            desc = a.get("description", "")
            src = a.get("source", {}).get("name", "")
            lines.append(f"{i+1}. {title} ({src})\n   {desc}")
        return "\n\n".join(lines)
    except Exception as e:
        return f"WebNews error: {e}"
