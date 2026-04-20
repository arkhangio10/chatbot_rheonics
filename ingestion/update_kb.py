"""
Incremental knowledge base updater.

This is the module that lets you add/update documents over time WITHOUT
re-processing everything. Core workflow:

    1. Drop new PDFs into /pdfs  (or new .md files into /my_notes)
    2. Run:  python -m ingestion.update_kb
    3. Only new or changed files are sent to Gemini.
    4. ChromaDB is updated incrementally.

How it decides what's "new":
    SHA-256 hash of each file is stored in .ingested.json
    A file is processed if:
      - It's not in the manifest, OR
      - Its hash differs from the stored hash (content changed)

Commands:
    python -m ingestion.update_kb              # Incremental update
    python -m ingestion.update_kb --force      # Re-process everything
    python -m ingestion.update_kb --status     # Show what's indexed
    python -m ingestion.update_kb --remove FILE.pdf  # Remove one file
"""

import os
import re
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

from ingestion.pdf_to_gemini import setup_gemini, process_pdf
from ingestion.build_vectorstore import (
    setup_gemini_embeddings,
    get_chroma_collection,
    flatten_json_file,
    upsert_chunks,
    delete_by_source,
    build_searchable_text,
    embed_texts,
)

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────

# Project root = parent of the ingestion/ folder this file lives in.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

PDFS_DIR = Path(os.environ.get("PDFS_DIR", PROJECT_ROOT / "pdfs"))
NOTES_DIR = Path(os.environ.get("NOTES_DIR", PROJECT_ROOT / "my_notes"))
KB_DIR = Path(os.environ.get("KNOWLEDGE_BASE_DIR", PROJECT_ROOT / "knowledge_base"))
MANIFEST_PATH = PROJECT_ROOT / ".ingested.json"


def _manifest_key(path: Path) -> str:
    """Stable, cwd-independent manifest key. Absolute, posix, lower-case drive."""
    return path.resolve().as_posix()


# ── Manifest I/O ─────────────────────────────────────────────────────────────

def load_manifest() -> dict:
    """Load the ingestion manifest (which files have been processed)."""
    if not MANIFEST_PATH.exists():
        return {"files": {}, "last_update": None}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest: dict):
    """Persist the manifest."""
    manifest["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def file_hash(path: Path) -> str:
    """Compute SHA-256 of a file for change detection."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Change detection ─────────────────────────────────────────────────────────

def scan_for_changes(force: bool = False) -> dict:
    """
    Compare filesystem against manifest and classify each file as:
      - 'new'       : never seen before
      - 'changed'   : seen before but content differs
      - 'unchanged' : already indexed, no changes
      - 'removed'   : in manifest but file no longer exists
    """
    manifest = load_manifest()
    known = manifest["files"]

    pdfs = list(PDFS_DIR.glob("*.pdf")) if PDFS_DIR.exists() else []
    notes = list(NOTES_DIR.glob("*.md")) if NOTES_DIR.exists() else []
    all_files = pdfs + notes

    classification = {"new": [], "changed": [], "unchanged": [], "removed": []}

    for f in all_files:
        key = _manifest_key(f)
        current_hash = file_hash(f)

        if force:
            classification["new" if key not in known else "changed"].append(f)
        elif key not in known:
            classification["new"].append(f)
        elif known[key]["hash"] != current_hash:
            classification["changed"].append(f)
        else:
            classification["unchanged"].append(f)

    # Detect removed files
    current_paths = {_manifest_key(f) for f in all_files}
    for tracked_path in known:
        if tracked_path not in current_paths:
            classification["removed"].append(Path(tracked_path))

    return classification


# ── Processing pipeline ─────────────────────────────────────────────────────

_NOTE_SLUG_RE = re.compile(r"[^a-z0-9]+")
_MAX_MD_CHUNK_CHARS = 1500


def _slugify(text: str) -> str:
    """Lowercase, ASCII-safe, dash-separated slug for use in chunk ids."""
    return _NOTE_SLUG_RE.sub("-", text.strip().lower()).strip("-") or "section"


def _split_markdown(text: str) -> list[tuple[str, str]]:
    """Split markdown on H2 (## ) headings; further split large sections on H3.

    Returns a list of (heading, body_including_heading) tuples. Content before
    the first H2 becomes a synthetic "intro" section.
    """
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_heading = "intro"
    current: list[str] = []

    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            if current:
                sections.append((current_heading, current))
            current_heading = line[3:].strip() or "section"
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append((current_heading, current))

    # Second pass: split any oversized section on H3 boundaries.
    out: list[tuple[str, str]] = []
    for heading, body_lines in sections:
        body = "\n".join(body_lines).strip()
        if len(body) <= _MAX_MD_CHUNK_CHARS:
            out.append((heading, body))
            continue

        sub_heading = heading
        sub_lines: list[str] = []
        sub_sections: list[tuple[str, str]] = []
        for line in body_lines:
            if line.startswith("### "):
                if sub_lines:
                    sub_sections.append((sub_heading, "\n".join(sub_lines).strip()))
                sub_heading = f"{heading} / {line[4:].strip()}"
                sub_lines = [line]
            else:
                sub_lines.append(line)
        if sub_lines:
            sub_sections.append((sub_heading, "\n".join(sub_lines).strip()))

        out.extend(sub_sections if len(sub_sections) > 1 else [(heading, body)])

    return [(h, b) for h, b in out if len(b) >= 30]


def process_note_file(note_path: Path, collection) -> int:
    """Split a markdown note by H2/H3 headings and upsert each section."""
    text = note_path.read_text(encoding="utf-8")
    if len(text.strip()) < 30:
        return 0

    sections = _split_markdown(text)
    if not sections:
        return 0

    chunks = []
    for idx, (heading, body) in enumerate(sections):
        chunks.append({
            "id": f"note_{note_path.stem}_{idx:02d}_{_slugify(heading)}",
            "text": body,
            "metadata": {
                "source": note_path.name,
                "page": idx + 1,
                "type": "notes",
                "products": "",
                "section": heading,
            },
        })

    return upsert_chunks(chunks, collection)


def process_pdf_file(pdf_path: Path, gemini_model, collection) -> tuple[int, list[int]]:
    """Run full pipeline for a single PDF: Gemini -> JSON -> embeddings -> ChromaDB.

    Returns (n_chunks_indexed, failed_page_numbers).
    """
    # 1. Remove any existing chunks from this source first
    removed = delete_by_source(pdf_path.name, collection)
    if removed:
        print(f"  Removed {removed} old chunks for {pdf_path.name}")

    # 2. Extract with Gemini
    result = process_pdf(pdf_path, gemini_model, KB_DIR)
    failed = result.get("metadata", {}).get("failed_pages", [])

    # 3. Flatten JSON and embed
    json_path = KB_DIR / f"{pdf_path.stem}.json"
    chunks = flatten_json_file(json_path)

    # 4. Upsert into ChromaDB
    n = upsert_chunks(chunks, collection)
    return n, failed


# ── Main update routine ─────────────────────────────────────────────────────

def update(force: bool = False) -> dict:
    """Main entry point: sync filesystem -> knowledge base."""
    print("Scanning for changes...")
    changes = scan_for_changes(force=force)

    print(f"  New:       {len(changes['new'])}")
    print(f"  Changed:   {len(changes['changed'])}")
    print(f"  Unchanged: {len(changes['unchanged'])}")
    print(f"  Removed:   {len(changes['removed'])}")

    to_process = changes["new"] + changes["changed"]
    if not to_process and not changes["removed"]:
        print("\nEverything is up to date. Nothing to do.")
        return changes

    # Setup Gemini + ChromaDB
    setup_gemini_embeddings()
    gemini_model = setup_gemini()
    _, collection = get_chroma_collection()

    manifest = load_manifest()

    # Handle removals
    for removed_file in changes["removed"]:
        print(f"\nRemoving: {removed_file.name}")
        n = delete_by_source(removed_file.name, collection)
        print(f"  Deleted {n} chunks")
        manifest["files"].pop(_manifest_key(removed_file), None)

    # Process PDFs and notes
    total_added = 0
    for f in to_process:
        print(f"\n-> {f.name}")
        try:
            failed_pages: list[int] = []
            if f.suffix.lower() == ".pdf":
                n, failed_pages = process_pdf_file(f, gemini_model, collection)
            elif f.suffix.lower() == ".md":
                n = process_note_file(f, collection)
            else:
                print(f"  Skipped (unsupported): {f.suffix}")
                continue

            total_added += n
            manifest["files"][_manifest_key(f)] = {
                "hash": file_hash(f),
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "chunks": n,
                "failed_pages": failed_pages,
            }
            print(f"  Indexed {n} chunks")

        except Exception as e:
            print(f"  ERROR: {e}")

    save_manifest(manifest)

    print(f"\nDone. Total chunks added/updated: {total_added}")
    print(f"Total files tracked: {len(manifest['files'])}")
    return changes


def show_status():
    """Print current knowledge base status."""
    manifest = load_manifest()
    _, collection = get_chroma_collection()

    print("=" * 60)
    print("Knowledge Base Status")
    print("=" * 60)
    print(f"Last update:      {manifest.get('last_update', 'never')}")
    print(f"Files tracked:    {len(manifest['files'])}")
    print(f"Chunks in store:  {collection.count()}")
    print()

    if not manifest["files"]:
        print("No files indexed yet. Drop PDFs in /pdfs and run update.")
        return

    print(f"{'File':<45} {'Chunks':>8}  {'Indexed':>22}  Failed")
    print("-" * 90)
    for path, info in sorted(manifest["files"].items()):
        name = Path(path).name
        chunks = info.get("chunks", "?")
        indexed = info.get("indexed_at", "?")[:19]
        failed = info.get("failed_pages") or []
        failed_str = ",".join(str(p) for p in failed) if failed else "-"
        print(f"{name:<45} {chunks:>8}  {indexed:>22}  {failed_str}")


def remove_file(source_name: str):
    """Manually remove a file's chunks from the KB (without deleting the source)."""
    setup_gemini_embeddings()
    _, collection = get_chroma_collection()

    n = delete_by_source(source_name, collection)
    print(f"Removed {n} chunks for {source_name}")

    manifest = load_manifest()
    matching = [p for p in manifest["files"] if Path(p).name == source_name]
    for p in matching:
        del manifest["files"][p]
    save_manifest(manifest)


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incremental KB updater")
    parser.add_argument("--force", action="store_true",
                       help="Re-process all files regardless of hash")
    parser.add_argument("--status", action="store_true",
                       help="Show what's currently indexed")
    parser.add_argument("--remove", type=str, metavar="FILE",
                       help="Remove chunks for a specific source file")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.remove:
        remove_file(args.remove)
    else:
        update(force=args.force)
