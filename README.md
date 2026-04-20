# Rheonics Support Chatbot

A RAG-based desktop chatbot for Rheonics technical support.

## Quick start

### 1. Clone & enter the project
```powershell
cd rheonics-chatbot
```

### 2. Create a virtual environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Set up your API keys
Copy `.env.example` to `.env` and fill in:
```
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_claude_key
```

### 5. Drop your PDFs
Place all Rheonics PDFs in the `/pdfs` folder.

### 6. Build the knowledge base
```powershell
python -m ingestion.update_kb
```

This scans `/pdfs` and `/my_notes`, processes only new/changed files, and
updates the vector store incrementally.

---

## Daily workflow

**When Rheonics releases new documentation:**
1. Drop the new PDFs into `/pdfs`
2. Run `python -m ingestion.update_kb`
3. That's it — only the new files get processed.

**When you write new personal notes:**
1. Save markdown files in `/my_notes`
2. Run `python -m ingestion.update_kb`

---

## Project docs

- [CLAUDE.md](./CLAUDE.md) — context file for AI assistants
- [docs/PRODUCT_BRIEF.md](./docs/PRODUCT_BRIEF.md) — what this product does
- [docs/SYSTEM_PROMPT.md](./docs/SYSTEM_PROMPT.md) — the chatbot's persona
- [docs/TEST_QUESTIONS.md](./docs/TEST_QUESTIONS.md) — evaluation benchmark
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) — how it all fits together

## Phase status

- ✅ Phase 0 — Planning complete
- 🔨 Phase 1 — Ingestion (in progress)
- ⏳ Phase 2 — Backend + Claude API
- ⏳ Phase 3 — Desktop UI
- ⏳ Phase 4 — Prompter integration
