# qa.py
import requests
from config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    DASHSCOPE_EMBED_MODEL,
    DASHSCOPE_EMBED_DIMS,
    DASHSCOPE_CHAT_MODEL,
    DB_DIR,
    CHROMA_COLLECTION_NAME,
)
import chromadb

# minimal embedding helper for queries (single)
def dashscope_embed(text):
    url = f"{DASHSCOPE_BASE_URL}/embeddings"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DASHSCOPE_EMBED_MODEL, "input": text, "dimensions": DASHSCOPE_EMBED_DIMS, "encoding_format": "float"}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"DashScope embed error: {r.status_code} {r.text}")
    data = r.json()
    return data["data"][0]["embedding"]

def dashscope_chat_completion(messages, max_tokens=512, temperature=0.2):
    url = f"{DASHSCOPE_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DASHSCOPE_CHAT_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"DashScope chat error: {r.status_code} {r.text}")
    return r.json()

class FinAgentQA:
    def __init__(self, top_k=4):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        self.collection = self.client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)
        self.top_k = top_k

    def query(self, user_query: str):
        q_emb = dashscope_embed(user_query)
        results = self.collection.query(query_embeddings=[q_emb], n_results=self.top_k, include=["documents", "metadatas", "distances"])
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context_parts = []
        for i, doc in enumerate(docs):
            src = metadatas[i].get("source", "unknown")
            snippet = doc[:800].replace("\n", " ")
            context_parts.append(f"[{i+1}] 来源: {src}\n{snippet}")

        context = "\n\n".join(context_parts)
        system_prompt = (
            "You are FinAgent Pro, a professional financial research assistant. "
            "Answer only using the provided context. Cite source indexes like [1]. "
            "If the context doesn't contain the answer, say 'No related data found in the provided materials.'"
        )
        user_prompt = f"User question: {user_query}\n\nContext:\n{context}"

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        resp = dashscope_chat_completion(messages, max_tokens=512, temperature=0.2)
        choices = resp.get("choices", [])
        if not choices:
            return ("", metadatas)
        first = choices[0]
        # support multiple response shapes
        if isinstance(first.get("message"), dict):
            answer = first["message"].get("content", "")
        else:
            answer = first.get("text", "") or ""
        return (answer, metadatas)
