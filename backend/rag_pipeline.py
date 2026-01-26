import hashlib
from typing import List

import requests
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.document_loader import DocumentLoadError, extract_text_from_bytes
from backend.embeddings import get_collection


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150
DEFAULT_TOP_K = 4
DEFAULT_LLM_MODEL = "mistral:7b-instruct"
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_COLLECTION_NAME = "documents"


def _document_id(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()


def _split_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
    )
    return splitter.split_text(text)


def _document_exists(collection, document_id: str) -> bool:
    existing = collection.get(where={"document_id": document_id}, limit=1)
    return len(existing.get("ids", [])) > 0


def index_document(file_bytes: bytes, filename: str) -> str:
    document_id = _document_id(file_bytes)
    collection = get_collection(DEFAULT_COLLECTION_NAME)
    if _document_exists(collection, document_id):
        return document_id

    text = extract_text_from_bytes(file_bytes, filename)
    if not text:
        raise DocumentLoadError("Document contains no readable text.")

    chunks = _split_text(text)
    ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": filename, "chunk": i, "document_id": document_id}
        for i in range(len(chunks))
    ]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return document_id


def _build_rag_prompt(context: str, question: str) -> str:
    return (
        "You are a helpful assistant. Answer using only the context. "
        "If the answer is not in the context, say you do not know.\n\n"
        f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"
    )


def _call_ollama_chat(model: str, prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a concise assistant."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    response = requests.post(url, json=payload, timeout=300)
    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")
    data = response.json()
    return data.get("message", {}).get("content", "").strip()


def answer_question_with_document_id(
    document_id: str, question: str, top_k: int = DEFAULT_TOP_K
) -> str:
    collection = get_collection(DEFAULT_COLLECTION_NAME)
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
        where={"document_id": document_id},
    )
    documents = results.get("documents", [[]])[0]
    context = "\n\n".join(documents) if documents else "No relevant context found."
    prompt = _build_rag_prompt(context, question)
    return _call_ollama_chat(DEFAULT_LLM_MODEL, prompt)
