"""
Build / update the ChromaDB vector store from extracted JSON chunks.

Takes the structured JSON files in /knowledge_base, builds a searchable
text representation of each page, generates embeddings with Gemini's
embedding model, and stores everything in ChromaDB.

Usage (as a module):
    from ingestion.build_vectorstore import upsert_chunks
    upsert_chunks(chunks, collection)
"""

import os
import json
import time
import random
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────

EMBEDDING_MODEL = os.environ.get("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./vector_store")
COLLECTION_NAME = "rheonics_docs"


# ── Client setup ─────────────────────────────────────────────────────────────

def get_chroma_collection():
    """Return (client, collection). Creates collection if it doesn't exist."""
    client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False),
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Rheonics technical documentation"},
    )
    return client, collection


def setup_gemini_embeddings(api_key: str | None = None):
    """Configure Gemini for embedding calls."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found")
    genai.configure(api_key=key)


# ── Chunk construction ──────────────────────────────────────────────────────

def build_searchable_text(chunk: dict) -> str:
    """Combine structured fields into a single searchable string."""
    parts = []

    if chunk.get("page_summary"):
        parts.append(f"Summary: {chunk['page_summary']}")

    if chunk.get("product_names"):
        parts.append(f"Products: {', '.join(chunk['product_names'])}")

    if chunk.get("extracted_text"):
        parts.append(chunk["extracted_text"])

    if chunk.get("specifications"):
        spec_lines = [f"{k}: {v}" for k, v in chunk["specifications"].items()]
        parts.append("Specifications:\n" + "\n".join(spec_lines))

    if chunk.get("key_facts"):
        parts.append("Key facts:\n" + "\n".join(f"- {f}" for f in chunk["key_facts"]))

    if chunk.get("diagram_labels"):
        parts.append(f"Diagram labels: {', '.join(chunk['diagram_labels'])}")

    if chunk.get("warnings_notes"):
        parts.append("Notes:\n" + "\n".join(f"- {w}" for w in chunk["warnings_notes"]))

    return "\n\n".join(parts).strip()


def flatten_json_file(json_path: Path) -> list[dict]:
    """Turn one extraction JSON file into a list of ChromaDB-ready docs."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat = []
    for chunk in data["chunks"]:
        text = build_searchable_text(chunk)
        if len(text) < 30:  # skip near-empty pages
            continue

        flat.append({
            "id": f"{data['source_file']}_p{chunk['page_num']}",
            "text": text,
            "metadata": {
                "source": data["source_file"],
                "page": chunk["page_num"],
                "type": chunk.get("document_type", "unknown"),
                "products": ", ".join(chunk.get("product_names", [])),
            },
        })
    return flat


# ── Embedding + upsert ──────────────────────────────────────────────────────

def _embed_one(text: str, max_attempts: int = 5) -> list[float]:
    """Embed a single text with exponential backoff on transient errors."""
    for attempt in range(max_attempts):
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(30.0, (2 ** attempt) + random.random())
            print(f"    Embedding retry {attempt + 1}/{max_attempts} after {delay:.1f}s: {e}")
            time.sleep(delay)
    raise RuntimeError("unreachable")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts (sequential with retries)."""
    return [_embed_one(t) for t in texts]


def upsert_chunks(chunks: list[dict], collection) -> int:
    """Add or update chunks in the ChromaDB collection."""
    if not chunks:
        return 0

    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print(f"  Generating {len(texts)} embeddings...")
    embeddings = embed_texts(texts)

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def delete_by_source(source_file: str, collection) -> int:
    """Remove all chunks associated with a given source PDF."""
    result = collection.get(where={"source": source_file})
    if not result["ids"]:
        return 0
    collection.delete(ids=result["ids"])
    return len(result["ids"])


# ── Full rebuild (rarely needed) ─────────────────────────────────────────────

def rebuild_from_knowledge_base(kb_dir: str | Path = "./knowledge_base"):
    """Rebuild the entire vector store from scratch. Use sparingly."""
    kb_dir = Path(kb_dir)
    setup_gemini_embeddings()
    client, collection = get_chroma_collection()

    # Drop existing collection
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Rheonics technical documentation"},
    )

    total = 0
    for json_file in kb_dir.glob("*.json"):
        print(f"Ingesting {json_file.name}...")
        chunks = flatten_json_file(json_file)
        n = upsert_chunks(chunks, collection)
        total += n

    print(f"\nTotal chunks indexed: {total}")


if __name__ == "__main__":
    rebuild_from_knowledge_base()
