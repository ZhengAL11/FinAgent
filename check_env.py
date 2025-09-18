try:
    import langchain
    import chromadb
    import streamlit
    import fastapi
    import pandas
    import pypdf
    import fitz   # pymupdf
    import unstructured
    import httpx
    print("✅ 所有核心依赖都已成功安装！")
except ImportError as e:
    print("❌ 缺少依赖：", e.name)
