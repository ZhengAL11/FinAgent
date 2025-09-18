# test_llm.py
from langchain_openai import ChatOpenAI  # ✅ 新写法
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_BASE, DEEPSEEK_MODEL

def test_deepseek():
    llm = ChatOpenAI(
        model=DEEPSEEK_MODEL,
        openai_api_base=DEEPSEEK_API_BASE,
        openai_api_key=DEEPSEEK_API_KEY,
    )

    query = "测试一下：用一句话总结大模型在金融研究中的价值。"
    resp = llm.invoke(query)
    print("✅ DeepSeek API 返回：", resp.content)

if __name__ == "__main__":
    test_deepseek()
