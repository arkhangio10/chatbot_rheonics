# Rheonics Support Chatbot — CLAUDE.md

This file is read by Claude Code (and Claude in chat) at the start of every
session. It's the single source of truth for project context.

---

## Project overview

A RAG-based desktop chatbot for Rheonics technical support.
- **User**: Abel Brayan Mancilla Montesinos (Support Engineer, Rheonics)
- **Status**: Phase 1 — Knowledge base ingestion
- **Purpose**: Answer technical questions about Rheonics products instantly,
  grounded only in official documentation.

## Stack

| Layer            | Technology              | Model / Version        |
|------------------|-------------------------|------------------------|
| PDF ingestion    | PyMuPDF + Gemini Vision | `gemini-2.5-flash`     |
| Embeddings       | Gemini Embedding API    | `gemini-embedding-001` |
| Vector store     | ChromaDB (local)        | latest                 |
| Backend          | FastAPI                 | Python 3.11+           |
| LLM (answers)    | Google Gemini           | `gemini-2.5-flash`     |
| Desktop UI       | Electron + React        | (Phase 3)              |

## Environment

- **OS**: Windows 11 / PowerShell
- **Python**: 3.11+
- **Machine**: Alienware m15 (2023), RTX GPU (used for future local models)
- **Execution**: Local development, no cloud deployment for MVP

## Folder structure

```
/rheonics-chatbot
├── /docs                  ← product brief, prompts, test questions
├── /ingestion             ← PDF + notes processing scripts
├── /backend               ← FastAPI server
├── /knowledge_base        ← JSON chunks from Gemini extraction
├── /vector_store          ← ChromaDB persisted data
├── /my_notes              ← manual markdown notes
├── /pdfs                  ← source PDFs (drop new docs here)
├── .env                   ← secrets (NEVER commit)
├── requirements.txt
└── CLAUDE.md              ← this file
```

## Rules for Claude

1. **Never invent Rheonics specifications.** Only use facts present in the
   knowledge base or provided documents. When unsure, say so.
2. **Stack discipline.** Don't suggest changing stack components mid-build
   unless asked. Current stack is frozen for Phase 1.
3. **Windows paths.** Use `pathlib.Path` and forward slashes in code for
   cross-platform safety.
4. **Environment first.** Always assume virtual environment. Never use
   `pip install` without `-r requirements.txt`.
5. **Ask before creating new folders or top-level files.**
6. **Naming.** Files use `snake_case`, classes use `PascalCase`.
7. **Commit hygiene.** Never commit: `.env`, `/vector_store/*`,
   `/knowledge_base/*.json` (these are generated artifacts).

## Current phase: Phase 1 — ✅ COMPLETE (2026-04-20)

**Goal**: Build the knowledge base. Get PDFs and notes into ChromaDB.

**Success criteria**:
- [x] All Rheonics PDFs processed through Gemini Vision
- [x] JSON chunks stored in `/knowledge_base`
- [x] Embeddings generated and stored in ChromaDB
- [x] `update_kb.py` can detect and ingest new files incrementally
- [ ] Retrieval quality validated against test questions  ← Phase 1.5

### Final ingestion stats (2026-04-20)

| Metric | Value |
|---|---|
| PDFs tracked | 292 |
| Notes tracked (`.md` in `/my_notes`) | 14 |
| Total chunks in ChromaDB | ~1,478 |
| PDF pages that failed RECITATION | ~25-30 (hard Gemini block, not bypassable via safety_settings) |
| Real cost to build | ~PEN 42 (~$11 USD) — 3× higher than Gemini's `usage_metadata` suggested |
| Wall time | ~90 min (1 s sleep between pages) |

### Lessons learned during Phase 1

1. **Gemini 2.5 Flash RECITATION filter** (`finish_reason=4`) silently blocks ~2-5 % of pages with boilerplate/standards text. Not adjustable via `safety_settings`. Current pipeline writes an empty stub and continues. Re-process those pages with a paraphrase prompt in a Phase 1.5 pass.
2. **Real cost ≈ 3× the counter**. `response.usage_metadata.prompt_token_count` under-reports (probably excludes image tokens). Watch **https://ai.studio/spend** for truth.
3. **Spend cap interacts badly with the manifest**: `save_manifest()` runs only at end of `update()`, so a mid-run 429 + Ctrl+C discards the manifest. Mitigation: `rebuild_manifest.py` (kept in project root) rebuilds it from `/knowledge_base/*.json`.
4. **PDFs with all-failed pages still end up in the manifest as `chunks=0, failed_pages=[...]`** → they're treated as "done" on re-run. Always run `rebuild_manifest.py` after a 429 crash so they get re-processed.
5. **`.md.html` files in `/pdfs`** (Rheonics engineering docs: rcp, error_codes, parameters, etc.) are not PDFs. `convert_html.py` extracts them to clean `.md` in `/my_notes` via html2text, then `update_kb.py` splits on H2/H3 headings.

### Helper scripts kept in project root

- `convert_html.py` — one-shot `.md.html` → `.md` converter (html2text)
- `rebuild_manifest.py` — regenerate `.ingested.json` from `/knowledge_base` after a crash
- `cleanup_failed.py` — purge manifest entries where every page failed (deprecated; use `rebuild_manifest.py` instead)

## Next phases (not now)

- **Phase 2**: FastAPI backend + Claude API answering
- **Phase 3**: Electron + React desktop UI
- **Phase 4**: Integration with Prompter app (Teams meeting context)

## Key references

- Product brief: `/docs/PRODUCT_BRIEF.md`
- System prompt: `/docs/SYSTEM_PROMPT.md`
- Test questions: `/docs/TEST_QUESTIONS.md`
- Architecture: `/docs/ARCHITECTURE.md`
