# agent_base.py
from typing import List, Dict, Any
from tools import search_reports_sync, calculate, web_news
from config import DASHSCOPE_CHAT_MODEL, DASHSCOPE_BASE_URL, DASHSCOPE_API_KEY
import requests
from dotenv import load_dotenv

load_dotenv()

# We implement a minimal Agent wrapper exposing .invoke(payload)
# payload expected: {"input": "<user question>", "messages": [ {"role":"user"/"assistant"/"system","content": "..."} ] }
class Agent:
    def __init__(self):
        # system prompt blueprint
        self.system_prompt = (
            "You are FinAgent Pro, a professional financial research assistant. "
            "Use provided context and tools when applicable, cite sources with [1],[2], etc. "
            "Do not hallucinate."
        )

    def _call_chat(self, messages: List[Dict[str, str]], max_tokens: int = 512, temperature: float = 0.2) -> str:
        url = f"{DASHSCOPE_BASE_URL}/chat/completions"
        headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": DASHSCOPE_CHAT_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code != 200:
            raise RuntimeError(f"Chat API error {r.status_code}: {r.text}")
        resp = r.json()
        choices = resp.get("choices", [])
        if not choices:
            return ""
        first = choices[0]
        if isinstance(first.get("message"), dict):
            return first["message"].get("content", "")
        else:
            return first.get("text", "") or ""

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        user_input = payload.get("input", "")
        history = payload.get("messages", []) or []

        # 1) tool decision heuristic (simple): if contains keywords, call tools
        # This is minimal — later replace with LangGraph decision logic
        tool_outputs = []
        # If user ask for "新闻" or "news", call web_news
        if any(k in user_input.lower() for k in ["新闻", "news", "latest", "recent"]):
            tool_out = web_news(user_input)
            tool_outputs.append({"tool": "web_news", "output": tool_out})

        # If user asks for comparison / specific numeric metric, call search_reports
        # We'll call search_reports to fetch supporting context for most queries
        sr = search_reports_sync(user_input)
        tool_outputs.append({"tool": "search_reports", "output": sr})

        # If the user asks a computation question (contains "增长" or "increase" or "%"), hint calculate usage
        # (We won't parse numbers here — the LLM can request calculation or we can parse numeric values later)
        # Append tool outputs to messages as system messages to provide context
        messages = [{"role": "system", "content": self.system_prompt}]
        # include previous history if any
        for m in history:
            if isinstance(m, dict) and "role" in m and "content" in m:
                messages.append(m)
        # Add tool outputs
        for t in tool_outputs:
            messages.append({"role": "system", "content": f"[Tool:{t['tool']}]: {t['output']}"})

        # Add user as last message
        messages.append({"role": "user", "content": user_input})

        # 2) call chat model
        try:
            answer = self._call_chat(messages)
        except Exception as e:
            answer = f"Chat call failed: {e}"

        # 3) return structure compatible with earlier usage
        # Provide updated messages history (append assistant)
        updated_messages = list(history)
        updated_messages.append({"role": "user", "content": user_input})
        updated_messages.append({"role": "assistant", "content": answer})

        return {"output": answer, "messages": updated_messages}

# export singleton agent
agent = Agent()


