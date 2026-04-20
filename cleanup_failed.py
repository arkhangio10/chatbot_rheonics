"""
Remove manifest entries for files where ingestion produced zero chunks
(i.e. every page hit an error). Next `update_kb` run will re-process them.

Also removes partial extraction JSON files so the pipeline starts clean.
"""
import json
from pathlib import Path

MANIFEST = Path(".ingested.json")
KB = Path("knowledge_base")

with open(MANIFEST, "r", encoding="utf-8") as f:
    m = json.load(f)

to_remove = []
for path, info in m["files"].items():
    if info.get("chunks", 0) == 0 and info.get("failed_pages"):
        to_remove.append(path)

print(f"Found {len(to_remove)} failed entries to purge:\n")
for p in to_remove:
    name = Path(p).name
    info = m["files"][p]
    print(f"  {name}  (failed pages: {info['failed_pages']})")
    # Remove matching JSON file so next run starts clean
    json_file = KB / f"{Path(p).stem}.json"
    if json_file.exists():
        json_file.unlink()
    del m["files"][p]

with open(MANIFEST, "w", encoding="utf-8") as f:
    json.dump(m, f, indent=2)

print(f"\nPurged. Manifest now tracks {len(m['files'])} files.")
print("Re-run: python -m ingestion.update_kb")
