# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------
# API Keys / Base URLs
# --------------------
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --------------------
# Model configuration
# --------------------
# Chat model (DashScope Qwen)
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen-plus-2025-09-11")
DASHSCOPE_CHAT_MODEL = CHAT_MODEL

# Embedding model
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-v4")
DASHSCOPE_EMBED_MODEL = EMBED_MODEL
DASHSCOPE_EMBED_DIMS = int(os.getenv("EMBED_DIMS", "1024"))

# --------------------
# Paths / DB
# --------------------
DATA_DIR = os.getenv("DATA_DIR", "data")
DB_DIR = os.getenv("DB_DIR", "db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "finagent")

# --------------------
# Ingest / runtime tuning
# --------------------
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "2000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# --------------------
# Quick checks (non-fatal)
# --------------------
def check_env():
    print("=== FinAgent Pro config loaded ===")
    if not DASHSCOPE_API_KEY:
        print("⚠️  Warning: DASHSCOPE_API_KEY is not set in .env")
    print(f"CHAT_MODEL={CHAT_MODEL}, EMBED_MODEL={EMBED_MODEL}, EMBED_DIMS={DASHSCOPE_EMBED_DIMS}")
    print(f"DATA_DIR={DATA_DIR}, DB_DIR={DB_DIR}, CHROMA_COLLECTION_NAME={CHROMA_COLLECTION_NAME}")
    print(f"BATCH_SIZE={BATCH_SIZE}, CHUNK_SIZE={CHUNK_SIZE}, CHUNK_OVERLAP={CHUNK_OVERLAP}")

check_env()
