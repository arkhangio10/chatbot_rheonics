"""
Rebuild .ingested.json from the JSON files that exist in /knowledge_base.

Why: a crash or Ctrl+C mid-run discards the manifest (save_manifest only runs
at the very end of update()). This script scans /knowledge_base, decides which
PDFs were legitimately processed, and writes manifest entries so the next
`update_kb` run skips them.

Rules:
  - JSON with at least one chunk that has extracted_text and NOT extraction_failed
      -> real success, write manifest entry with current PDF hash
  - JSON where every chunk has extraction_failed=True (or file is empty/missing)
      -> delete the JSON so next run re-processes from scratch
"""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
KB = PROJECT_ROOT / "knowledge_base"
PDFS = PROJECT_ROOT / "pdfs"
NOTES = PROJECT_ROOT / "my_notes"
MANIFEST = PROJECT_ROOT / ".ingested.json"


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_key(path: Path) -> str:
    return path.resolve().as_posix()


manifest = {"files": {}, "last_update": datetime.now(timezone.utc).isoformat()}

good = 0
purged = 0
skipped = 0

for json_file in sorted(KB.glob("*.json")):
    pdf_name = json_file.stem + ".pdf"
    pdf_path = PDFS / pdf_name

    if not pdf_path.exists():
        print(f"  ? No matching PDF for {json_file.name} (skipped)")
        skipped += 1
        continue

    try:
        data = json.loads(json_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  ! Unreadable JSON {json_file.name}: {e}  -> delete")
        json_file.unlink()
        purged += 1
        continue

    chunks = data.get("chunks", [])
    successful = [c for c in chunks if not c.get("extraction_failed") and c.get("extracted_text")]
    failed_pages = [c["page_num"] for c in chunks if c.get("extraction_failed")]

    if not successful:
        print(f"  X {json_file.name}: all {len(chunks)} pages failed -> delete")
        json_file.unlink()
        purged += 1
        continue

    manifest["files"][manifest_key(pdf_path)] = {
        "hash": file_hash(pdf_path),
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "chunks": len(successful),
        "failed_pages": failed_pages,
    }
    good += 1
    tag = f" (failed: {failed_pages})" if failed_pages else ""
    print(f"  OK {pdf_name}  {len(successful)} chunks{tag}")

# NOTE: .md notes in my_notes are not tracked here (they have no JSON file).
# They will be re-embedded on next run, which is cheap (~$0.01 total for all).

with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"\nSummary:")
print(f"  {good} PDFs written to manifest (will be SKIPPED on re-run)")
print(f"  {purged} JSON files purged (PDFs will be RE-PROCESSED)")
print(f"  {skipped} unmatched JSONs")
print(f"\nManifest saved: {MANIFEST}")
print("Next step:  python -m ingestion.update_kb")
