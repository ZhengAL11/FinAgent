# search_test.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
from config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    DASHSCOPE_CHAT_MODEL,
    DASHSCOPE_EMBED_MODEL,
    CHROMA_DB_DIR,
)
import chromadb

def dashscope_embed(text):
    url = f"{DASHSCOPE_BASE_URL}/embeddings"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DASHSCOPE_EMBED_MODEL, "input": text, "dimensions": 1024, "encoding_format": "float"}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]

def dashscope_chat_completion(messages, max_tokens=512, temperature=0.0):
    url = f"{DASHSCOPE_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {DASHSCOPE_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": DASHSCOPE_CHAT_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()

def build_chroma_client():
    client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = client.get_or_create_collection(name="finagent")
    return collection

def answer_query(user_query, top_k=4):
    collection = build_chroma_client()
    q_emb = dashscope_embed(user_query)
    results = collection.query(query_embeddings=[q_emb], n_results=top_k, include=["documents", "metadatas", "distances"])
    docs = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n".join([f"[{i+1}] 来源: {metadatas[i].get('source','unknown')}\n{docs[i]}" for i in range(len(docs))])

    system_prompt = "你是金融研究助理，请仅根据以下材料回答问题，并在结论后用 [编号] 标注来源。"
    user_prompt = f"用户问题：{user_query}\n\n参考材料：\n{context}"

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    resp = dashscope_chat_completion(messages)
    choices = resp.get("choices", [])
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    return {"answer": content, "sources": metadatas}

if __name__ == "__main__":
    q = "中芯国际的利润总额是多少？"
    out = answer_query(q)
    print("\n问题:", q)
    print("\n答案:\n", out["answer"])
    print("\n参考来源：")
    for i, md in enumerate(out["sources"]):
        print(f"- [{i+1}] {md.get('source','unknown')}")
