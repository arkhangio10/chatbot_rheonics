# Architecture

## High-level flow

```
┌──────────────────────────────────────────────────────────────┐
│                    PHASE 1 — INGESTION                        │
└──────────────────────────────────────────────────────────────┘

 /pdfs/*.pdf           /my_notes/*.md
      │                     │
      ▼                     │
 ┌─────────────────┐        │
 │ pdf_to_gemini   │        │
 │ (Gemini Vision) │        │
 └────────┬────────┘        │
          │                 │
          ▼                 ▼
 /knowledge_base/*.json (structured chunks)
          │
          ▼
 ┌─────────────────────┐
 │ build_vectorstore   │  ← uses gemini-embedding-001
 └──────────┬──────────┘
            ▼
    ┌───────────────┐
    │   ChromaDB    │  (persisted in /vector_store)
    └───────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    PHASE 2 — ANSWERING                        │
└──────────────────────────────────────────────────────────────┘

 User question
      │
      ▼
 ┌─────────────────┐
 │   FastAPI       │
 │   /query        │
 └────────┬────────┘
          ▼
 ┌─────────────────┐
 │   retriever.py  │  → top-k chunks from ChromaDB
 └────────┬────────┘
          ▼
 ┌─────────────────┐
 │   llm.py        │  → Gemini 2.5 Flash with system prompt
 └────────┬────────┘
          ▼
   Grounded answer

┌──────────────────────────────────────────────────────────────┐
│                    PHASE 3 — DESKTOP UI                       │
└──────────────────────────────────────────────────────────────┘

   Electron window (React) ──HTTP──► FastAPI backend
```

## Component responsibilities

### `/ingestion`

- **`pdf_to_gemini.py`** — Converts PDFs to images, sends each page to
  Gemini 2.5 Flash, saves structured JSON chunks to `/knowledge_base`.
- **`build_vectorstore.py`** — Reads JSON chunks, generates embeddings
  with `gemini-embedding-001`, stores them in ChromaDB.
- **`update_kb.py`** — The update module. Scans `/pdfs` and `/my_notes`,
  detects new or changed files via SHA-256 hash, runs only needed steps.
  Maintains `.ingested.json` manifest.

### `/backend`

- **`main.py`** — FastAPI app with endpoints: `/query`, `/health`,
  `/kb/status`.
- **`retriever.py`** — ChromaDB client wrapper. Top-k semantic search.
- **`llm.py`** — Anthropic Claude wrapper. Builds prompt from system
  prompt + context + user question.

### `/docs`

Human-writable documentation. The system prompt, test questions, and
product brief live here and are version-controlled.

## Data contracts

### Chunk JSON (produced by ingestion)

```json
{
  "source_file": "SRD_datasheet.pdf",
  "total_pages": 6,
  "chunks": [
    {
      "page_num": 1,
      "page_summary": "SRD product overview and specifications",
      "document_type": "datasheet",
      "product_names": ["SRD", "SME-TRD"],
      "extracted_text": "...",
      "specifications": { "viscosity_range": "1 to 3000 cP" },
      "key_facts": ["..."],
      "diagram_labels": ["..."],
      "warnings_notes": ["..."]
    }
  ]
}
```

### ChromaDB document

```python
{
  "id": "SRD_datasheet.pdf_p1",
  "document": "<full text representation>",
  "embedding": [0.01, -0.23, ...],
  "metadata": {
    "source": "SRD_datasheet.pdf",
    "page": 1,
    "type": "datasheet",
    "products": "SRD, SME-TRD"
  }
}
```

### Query API response (Phase 2)

```json
{
  "answer": "The SRD measures viscosity from 1 to 3,000 cP...",
  "sources": [
    { "file": "SRD_datasheet.pdf", "page": 1 }
  ],
  "confidence": "high"
}
```
