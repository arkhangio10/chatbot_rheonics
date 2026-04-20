"""
Retriever: semantic search over the ChromaDB vector store.

Given a user question, returns the top-k most relevant document chunks.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

from ingestion.build_vectorstore import get_chroma_collection

load_dotenv()

EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")


def _ensure_gemini_configured():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=key)


def embed_query(query: str) -> list[float]:
    """Generate an embedding for a user query."""
    _ensure_gemini_configured()
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="retrieval_query",  # different from retrieval_document
    )
    return result["embedding"]


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k chunks most relevant to the query."""
    _, collection = get_chroma_collection()
    query_embedding = embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if results.get("distances") else None,
        })

    return chunks


def format_chunks_for_prompt(chunks: list[dict]) -> str:
    """Build the context block injected into the Claude prompt."""
    formatted = []
    for i, chunk in enumerate(chunks, 1):
        src = chunk["metadata"].get("source", "unknown")
        page = chunk["metadata"].get("page", "?")
        formatted.append(
            f"--- Source {i}: {src} (page {page}) ---\n{chunk['text']}"
        )
    return "\n\n".join(formatted)
