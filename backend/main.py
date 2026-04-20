"""
FastAPI backend for the Rheonics chatbot.

Run with:
    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.retriever import retrieve, format_chunks_for_prompt
from backend.llm import answer_question
from ingestion.build_vectorstore import get_chroma_collection
from ingestion.update_kb import load_manifest

app = FastAPI(title="Rheonics Support Chatbot", version="0.1.0")

# Allow Electron frontend to talk to this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / response schemas ───────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str
    k: int = 5  # number of chunks to retrieve


class SourceRef(BaseModel):
    file: str
    page: int


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceRef]
    retrieved_chunks: int
    model: str


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/kb/status")
def kb_status():
    """Knowledge base status — how many docs, how many chunks, last update."""
    manifest = load_manifest()
    _, collection = get_chroma_collection()
    return {
        "files_tracked": len(manifest["files"]),
        "chunks_indexed": collection.count(),
        "last_update": manifest.get("last_update"),
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """Main endpoint: retrieve + answer."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")

    try:
        chunks = retrieve(req.question, k=req.k)
        if not chunks:
            return QueryResponse(
                answer="I don't have enough information in my documents to answer this.",
                sources=[],
                retrieved_chunks=0,
                model="none",
            )

        context_block = format_chunks_for_prompt(chunks)
        result = answer_question(req.question, context_block)

        sources = [
            SourceRef(
                file=c["metadata"].get("source", "unknown"),
                page=c["metadata"].get("page", 0),
            )
            for c in chunks
        ]

        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            retrieved_chunks=len(chunks),
            model=result["model"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
