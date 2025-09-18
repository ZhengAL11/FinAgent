# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# DashScope (阿里云百炼) 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 你已提供的 base_url
DASHSCOPE_EMBED_MODEL = "text-embedding-v4"
DASHSCOPE_EMBED_DIMS = 1024  # 可选：64/128/256/512/768/1024/1536/2048，默认1024

# LLM（如果你想用百炼的 Chat 模型）
DASHSCOPE_CHAT_MODEL = "qwen-plus-2025-09-11"  # 你提供的示例模型名，按需替换

# Chroma 持久化目录
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")

# 校验
if not DASHSCOPE_API_KEY:
    raise ValueError("请先在 .env 中设置 DASHSCOPE_API_KEY")
