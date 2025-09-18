# ingest.py
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()
from config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    DASHSCOPE_EMBED_MODEL,
    DASHSCOPE_EMBED_DIMS,
    CHROMA_DB_DIR,
)
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

DATA_DIR = "data"
BATCH_SIZE = 10
CHUNKSIZE = 2000
CHUNK_OVERLAP = 200

def dashscope_embed_batch(texts):
    url = f"{DASHSCOPE_BASE_URL}/embeddings"
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DASHSCOPE_EMBED_MODEL,
        "input": texts,
        "dimensions": DASHSCOPE_EMBED_DIMS,
        "encoding_format": "float"
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code != 200:
        print("DashScope embedding failed:", resp.status_code, resp.text)
        resp.raise_for_status()
    data = resp.json()
    return [item["embedding"] for item in data.get("data", [])]

def load_pdfs_set_source(data_dir):
    docs = []
    for fname in os.listdir(data_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(data_dir, fname)
        loader = PyMuPDFLoader(path)
        loaded = loader.load()
        for d in loaded:
            d.metadata["source"] = fname
        docs.extend(loaded)
        print(f"✅ 加载: {fname}, 段数: {len(loaded)}")
    return docs

def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNKSIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)
    print(f"✂️ 切分完成，总段数: {len(chunks)}")
    return chunks

def build_or_update_chroma(chunks):
    texts = [d.page_content for d in chunks]
    metadatas = [d.metadata for d in chunks]
    ids = [f"{md.get('source','doc')}_{i}" for i, md in enumerate(metadatas)]

    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="finagent")

    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        emb_batch = dashscope_embed_batch(batch)
        embeddings.extend(emb_batch)
        time.sleep(0.5)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print(f"✅ 写入 Chroma 成功，条数: {len(texts)}，路径: {CHROMA_DB_DIR}")

if __name__ == "__main__":
    docs = load_pdfs_set_source(DATA_DIR)
    chunks = chunk_documents(docs)
    build_or_update_chroma(chunks)
