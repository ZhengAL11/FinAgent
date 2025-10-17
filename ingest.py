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
    DATA_DIR,
    DB_DIR,
    CHROMA_COLLECTION_NAME,
    BATCH_SIZE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

# langchain loaders / text splitter
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import chromadb
from chromadb.config import Settings

# ensure DB dir exists
os.makedirs(DB_DIR, exist_ok=True)

# ---------- DashScope embedding wrapper ----------
def dashscope_embed_batch(texts, max_retries=3, backoff=1.0):
    """
    texts: list of strings (1..BATCH_SIZE)
    returns: list of embeddings (lists of floats)
    """
    assert isinstance(texts, list) and len(texts) > 0
    url = f"{DASHSCOPE_BASE_URL}/embeddings"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": DASHSCOPE_EMBED_MODEL,
        "input": texts,
        "dimensions": DASHSCOPE_EMBED_DIMS,
        "encoding_format": "float",
    }

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                resp = r.json()
                data = resp.get("data", [])
                embeddings = [item["embedding"] for item in data]
                if len(embeddings) != len(texts):
                    raise RuntimeError("Embedding count mismatch")
                return embeddings
            else:
                # retry on rate limit or server errors
                if r.status_code in (429, 500, 502, 503, 504):
                    print(f"[dashscope] status {r.status_code}, retrying (attempt {attempt})")
                    time.sleep(backoff * attempt)
                    continue
                else:
                    r.raise_for_status()
        except requests.RequestException as e:
            print(f"[dashscope] request exception: {e}; attempt {attempt}")
            time.sleep(backoff * attempt)
    raise RuntimeError("DashScope embedding failed after retries")

# ---------- PDF loading & chunking ----------
def load_pdfs(data_dir=DATA_DIR):
    docs = []
    if not os.path.exists(data_dir):
        print(f"[ingest] data dir not found: {data_dir}")
        return docs
    for fname in sorted(os.listdir(data_dir)):
        if not fname.lower().endswith(".pdf"):
            continue
        fp = os.path.join(data_dir, fname)
        loader = PyMuPDFLoader(fp)
        loaded = loader.load()  # list of Document
        # attach source filename metadata
        for d in loaded:
            md = d.metadata or {}
            md["source"] = fname
            d.metadata = md
        print(f"[ingest] Loaded {fname}: {len(loaded)} raw pages/blocks")
        docs.extend(loaded)
    return docs

def chunk_documents(docs, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    print(f"[ingest] Chunked into {len(chunks)} segments")
    return chunks

# ---------- Chroma upsert ----------
def build_or_update_chroma(chunks):
    if not chunks:
        print("[ingest] no chunks to index, exit.")
        return

    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [f"{md.get('source','doc')}_{i}" for i, md in enumerate(metadatas)]

    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        print(f"[ingest] embedding batch {i//BATCH_SIZE + 1} size={len(batch)}")
        emb = dashscope_embed_batch(batch)
        embeddings.extend(emb)
        time.sleep(0.2)

    if len(embeddings) != len(texts):
        raise RuntimeError("embeddings/texts length mismatch")

    # Use collection.add (chroma v0.14+ API uses .add)
    print("[ingest] upserting into Chroma...")
    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    print(f"[ingest] Indexed {len(texts)} chunks into {DB_DIR}")

if __name__ == "__main__":
    print("=== FinAgent Pro: ingest.py ===")
    docs = load_pdfs(DATA_DIR)
    if not docs:
        print("[ingest] no PDF loaded - place PDFs under data/ and retry.")
        raise SystemExit(1)
    chunks = chunk_documents(docs)
    # debug preview
    for i, c in enumerate(chunks[:2]):
        print(f"--- preview chunk {i} ---\n{c.page_content[:200]}\n")
    build_or_update_chroma(chunks)
    print("=== ingest finished ===")
