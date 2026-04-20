"""
One-shot converter: .md.html / .json.html in /pdfs  ->  clean .md in /my_notes
Run once, then delete. Not part of the ingestion pipeline.
"""
import html2text
from pathlib import Path

src = Path("pdfs")
dst = Path("my_notes")
dst.mkdir(exist_ok=True)

h = html2text.HTML2Text()
h.ignore_links = False
h.body_width = 0  # don't wrap lines

files = list(src.glob("*.md.html")) + list(src.glob("*.json.html"))

for f in files:
    name = f.name.replace(".md.html", ".md").replace(".json.html", ".md")
    md = h.handle(f.read_text(encoding="utf-8"))
    (dst / name).write_text(md, encoding="utf-8")
    print(f"  -> my_notes/{name}  ({len(md):,} chars)")

print(f"\nDone: {len(files)} files")
