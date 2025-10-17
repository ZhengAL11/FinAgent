# main_app.py
import streamlit as st
from agent_base import agent  # 导入你的智能体核心逻辑

st.set_page_config(page_title="FinAgent Pro", layout="wide")

st.title("💼 FinAgent Pro - 财报智能体助手")
st.caption("企业级财报分析智能体 · 支持多轮对话 + 知识增强 + 实时检索")

# 聊天记录
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 展示历史记录
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 用户输入区
user_input = st.chat_input("请输入问题，例如：宁德时代2025年研发投入是多少？")

if user_input:
    # 显示用户消息
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 智能体回答
    with st.chat_message("assistant"):
        with st.spinner("FinAgent 正在分析数据..."):
            try:
                response = agent(user_input)
                st.markdown(response)
                st.session_state["messages"].append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"发生错误：{e}")
