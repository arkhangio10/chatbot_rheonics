# Rheonics Support Chatbot — Implementation Plan

**Owner:** Abel · **Date:** 2026-04-18 · **Status:** Phase 1 starting

---

## Decisions locked on 2026-04-18

1. **System prompt source of truth:** `docs/SYSTEM_PROMPT.md`.
   `backend/llm.py` loads and templates it; no inline copy.
2. **Answering LLM:** Gemini 2.5 Flash. **Anthropic Claude removed from
   the stack.** One provider (Google) for ingestion, embeddings, and
   answering — cheaper, faster, simpler key management.
3. **PDFs:** Abel drops them into `/pdfs` manually.

Stack table in `CLAUDE.md` will be updated to reflect (2).

---

## Phase 1 — Ingestion (CURRENT)

**Goal:** A working, incremental pipeline from `/pdfs` + `/my_notes` to a
queryable ChromaDB, validated against `TEST_QUESTIONS.md` at ≥80% retrieval
recall.

### Step 1.1 — Stack swap: Claude → Gemini 2.5 Flash

Files to modify:
- `backend/llm.py` — replace `anthropic` client with
  `google.generativeai.GenerativeModel(GEMINI_ANSWER_MODEL,
   system_instruction=<loaded prompt>)`. Keep the same
  `answer_question(question, context_block) -> dict` signature so
  `main.py` doesn't change.
- `.env.example` — remove `ANTHROPIC_API_KEY` and `CLAUDE_MODEL`, add
  `GEMINI_ANSWER_MODEL=gemini-2.5-flash`.
- `requirements.txt` — remove `anthropic>=0.39.0`.
- `CLAUDE.md` stack table row "LLM (answers)" → `Gemini 2.5 Flash`.
- `docs/ARCHITECTURE.md:48` — rename the `llm.py` arrow label from
  "Claude Sonnet" to "Gemini 2.5 Flash".

### Step 1.2 — System prompt as single source of truth

- `backend/llm.py::load_system_prompt()` reads `docs/SYSTEM_PROMPT.md`
  and extracts the fenced code block between the `## Current version`
  section markers.
- Template `{retrieved_chunks}` in the **user message**, not the system
  message (Gemini handles system instructions separately). Remove the
  `## Context` / `## User question` sections from the system text
  before sending.
- Version string passed through in the response payload.

### Step 1.3 — Ingestion bug fixes

Targeted, no refactor:

| File : line | Fix |
|---|---|
| `ingestion/update_kb.py:51` | Anchor `MANIFEST_PATH` to the project root (`Path(__file__).resolve().parents[1] / ".ingested.json"`). |
| `ingestion/update_kb.py:100` | Normalize manifest keys with `f.resolve().as_posix()`. Migrate any existing manifest on first run. |
| `ingestion/update_kb.py:66,207` | `datetime.utcnow()` → `datetime.now(timezone.utc)`. |
| `ingestion/pdf_to_gemini.py:19` | Remove unused `import base64`. |
| `ingestion/build_vectorstore.py:169` | Pass `metadata={...}` on the recreate call inside `rebuild_from_knowledge_base`. |
| `ingestion/build_vectorstore.py:112-122` | Add a simple exponential-backoff retry wrapper on `genai.embed_content` for 429/503. One-at-a-time loop stays (Gemini embedding API does not batch reliably yet); concurrency via `ThreadPoolExecutor(max_workers=4)` is the right first step. |

### Step 1.4 — Observability for failed pages

`ingestion/pdf_to_gemini.py` currently produces a silent empty stub on
failure (lines 118-129). Extend the saved JSON `metadata` block with a
`failed_pages: [page_num, ...]` list so `update_kb --status` can surface
it and Abel knows to re-run a specific page.

### Step 1.5 — Markdown notes chunking

`ingestion/update_kb.py:123-139` turns a whole `.md` file into one chunk
— fine for short notes, terrible for long ones. Replace with:

- Split on H2 (`## `) headings; if a section is still >1500 chars, split
  on H3.
- Chunk id: `note_<stem>_<section-slug>`.
- Metadata keeps `source` = filename; add `section` = heading text.

### Step 1.6 — First ingestion run

1. Abel drops initial PDFs into `/pdfs` (start small: 3-5 datasheets to
   smoke-test the pipeline before bulk ingestion).
2. Fill `.env` from `.env.example`.
3. `python -m ingestion.update_kb`
4. `python -m ingestion.update_kb --status` to confirm counts.

### Step 1.7 — Retrieval evaluation

New file `backend/evaluate.py` (small, ~80 lines):

- Parses `docs/TEST_QUESTIONS.md`, extracts `question` and
  `key facts` columns.
- For each question, calls `retrieve(question, k=5)` and checks whether
  any key fact substring appears in the top-k chunks' text.
- Prints a pass/fail table and pass rate.
- Writes a row to the "Results log" table in `TEST_QUESTIONS.md`
  (manually for now; automated later).

**Gate:** Phase 1 is done when retrieval recall ≥ 80% on the 20
questions. If below, iterate on: chunk construction
(`build_searchable_text`), extraction prompt, or chunk sizing.

---

## Phase 2 — Answering backend

**Goal:** End-to-end `/query` with grounded, cited answers using
Gemini 2.5 Flash.

### Step 2.1 — Wire `llm.py` into `/query`

Already scaffolded in `backend/main.py`. After Phase 1.1-1.2 the flow is
complete. Verify:

- `POST /query` with `{"question": "..."}` returns answer + sources.
- `GET /kb/status` reflects current counts.
- `GET /health` returns `{"status": "ok"}`.

### Step 2.2 — Full answer-quality evaluation

Extend `backend/evaluate.py` to optionally run the LLM and judge:

- Direct answer contains expected key facts (pass).
- Answer cites a source (soft check for "According to", filename, or
  page).
- Edge cases 18-20 produce the expected refusal / clarification.

Target: 80% pass on all 20 questions.

### Step 2.3 — Latency and cost measurement

Log `response.usage` per query; measure p50/p95 over a 20-question run.
Target `<3s` p95. If Flash is too slow, try `gemini-2.5-flash-lite`.

### Step 2.4 — Minor hardening

- `retriever.py:52` — guard against empty `distances` list.
- `main.py:101-102` — return a structured error instead of bare 500.
- Streaming responses (`/query/stream`) — deferred unless needed for UX.

---

## Phase 3 — Desktop UI (Electron + React)

**Goal:** Minimal chat window Abel can keep open during Teams calls.

### Step 3.1 — Scaffold

- `electron-vite` + React + TypeScript in a new `/desktop` folder.
- Main process: window + menu; no file system access needed.
- Renderer: single-page chat view.

### Step 3.2 — Chat UI

- Message list (user ↔ assistant bubbles).
- Input box with Enter-to-send, Shift-Enter for newline.
- Source chips below each answer (`SRD_datasheet.pdf p.2`),
  click-to-reveal the retrieved chunk.
- KB status bar at the bottom (pulls from `/kb/status`).

### Step 3.3 — Backend communication

- HTTP to `http://localhost:8000` (FastAPI already has CORS `*`).
- Simple fetch wrapper; no auth for MVP.
- On app start, health-check the backend; if down, show a
  "Start the backend" banner with the exact command.

### Step 3.4 — Packaging

- `electron-builder` → Windows `.exe` installer (Abel's OS).
- Bundled backend launcher **not** in Phase 3; user runs
  `uvicorn backend.main:app` in a terminal. Bundling comes later.

---

## Phase 4 — Prompter integration

**Goal:** Inject live client context (fluid type, industry,
operating conditions) from the Prompter app into every query so answers
become client-specific instead of generic.

### Step 4.1 — Context contract

Define a JSON shape Prompter pushes:

```json
{
  "client": "Acme Drilling",
  "fluid": "synthetic mud",
  "industry": "drilling",
  "conditions": { "temp_c": 85, "pressure_bar": 120 }
}
```

### Step 4.2 — Transport

Prompter → chatbot: local HTTP `POST /context` sets a session-level
context that `/query` prepends to the user message until cleared with
`DELETE /context`.

### Step 4.3 — System prompt update

New section in `SYSTEM_PROMPT.md` (v2.0) teaching the model to use
client context when present: "Before answering, check if any product
limitations exclude this client's conditions."

### Step 4.4 — Session memory (was "out of scope Phase 1")

Introduce per-session conversation history (in-memory, not persisted)
so follow-up questions work naturally.

---

## Risks and non-goals

- **Not building:** cloud deployment, authentication, multi-user, PDF
  editing, live sensor integration, pricing, competitor info.
- **Known risk:** Gemini free-tier rate limits will bite on bulk
  ingestion. Mitigation: `sleep_between=1.0` already present in
  `process_pdf`; can be raised if 429s appear.
- **Known risk:** Rheonics documentation has overlapping product
  families (SRD vs SRV vs SMET). Retrieval must disambiguate — if
  cross-product contamination shows up in eval, add a
  `product_names` filter in `retriever.retrieve()`.

---

## Verification checklist (end of Phase 1)

- [ ] `python -m ingestion.update_kb` runs clean on an empty state with
      3 test PDFs.
- [ ] Re-running it with no new files reports "Everything is up to date"
      and does not call Gemini.
- [ ] Adding one new PDF only processes that one file.
- [ ] Deleting a PDF from `/pdfs` and re-running removes its chunks
      from ChromaDB.
- [ ] `python -m ingestion.update_kb --status` shows correct counts.
- [ ] `python -m backend.evaluate` prints ≥80% retrieval pass rate on
      20 questions.
- [ ] No `anthropic` import remains anywhere in the repo.
- [ ] `backend/llm.py` loads the prompt from `docs/SYSTEM_PROMPT.md`
      and uses Gemini 2.5 Flash.
