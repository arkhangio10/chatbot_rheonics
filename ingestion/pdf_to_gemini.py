"""
PDF → Images → Gemini 2.5 Flash Vision → Structured JSON chunks.

This module handles the first half of ingestion: turning raw PDFs into
clean, structured text chunks that can later be embedded and indexed.

Usage (as a module):
    from ingestion.pdf_to_gemini import process_pdf, setup_gemini
    model = setup_gemini(api_key)
    result = process_pdf("pdfs/SRD.pdf", model, "knowledge_base")

Usage (as a script, for debugging a single file):
    python -m ingestion.pdf_to_gemini --pdf pdfs/SRD.pdf
"""

import os
import json
import time
import argparse
import io
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ────────────────────────────────────────────────────────────

GEMINI_MODEL = os.environ.get("GEMINI_VISION_MODEL", "gemini-2.5-flash")

# Gemini 2.5 Flash pricing (USD per 1M tokens)
PRICE_INPUT_PER_MTOK = float(os.environ.get("GEMINI_FLASH_PRICE_IN", "0.30"))
PRICE_OUTPUT_PER_MTOK = float(os.environ.get("GEMINI_FLASH_PRICE_OUT", "2.50"))

# Module-level running totals (persist across PDFs in a single run)
_run_totals = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "pages": 0}


def _cost(in_tok: int, out_tok: int) -> float:
    return in_tok / 1_000_000 * PRICE_INPUT_PER_MTOK + out_tok / 1_000_000 * PRICE_OUTPUT_PER_MTOK


def get_run_totals() -> dict:
    """Return current cumulative usage/cost since module import."""
    return dict(_run_totals)

EXTRACTION_PROMPT = """You are a technical document analyst for Rheonics, a company
that makes inline viscometers and density sensors.

Analyze this page and extract ALL information you can see. Be thorough.

Return ONLY a JSON object (no markdown fences, no commentary) with this shape:
{
  "page_summary": "one sentence description of this page",
  "document_type": "datasheet|manual|drawing|presentation|whitepaper|notes",
  "product_names": ["list of products mentioned"],
  "extracted_text": "all readable text, preserving logical structure",
  "specifications": { "key": "value with units" },
  "key_facts": ["important facts as complete sentences"],
  "diagram_labels": ["labels found in diagrams, drawings, or charts"],
  "warnings_notes": ["warnings, compliance notes, or cautions"]
}

If a field has no relevant content, return an empty list or empty string."""


# ── Core functions ───────────────────────────────────────────────────────────

def setup_gemini(api_key: str | None = None):
    """Initialize the Gemini client."""
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found in environment or .env")
    genai.configure(api_key=key)
    return genai.GenerativeModel(GEMINI_MODEL)


def pdf_to_images(pdf_path: str | Path, dpi: int = 200) -> list[dict]:
    """Convert each page of a PDF to a PIL image."""
    pdf_path = Path(pdf_path)
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        pages.append({
            "page_num": page_num + 1,
            "image": img,
            "width": pix.width,
            "height": pix.height,
        })

    doc.close()
    return pages


def extract_page_with_gemini(model, page_data: dict, retry: int = 2) -> dict:
    """Send one page image to Gemini and parse structured output."""
    img = page_data["image"]

    for attempt in range(retry + 1):
        try:
            response = model.generate_content([EXTRACTION_PROMPT, img])
            raw = response.text.strip()

            # Strip markdown fences if Gemini added them
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            extracted = json.loads(raw)
            extracted["page_num"] = page_data["page_num"]

            # Track usage + running cost
            usage = getattr(response, "usage_metadata", None)
            in_tok = getattr(usage, "prompt_token_count", 0) or 0
            out_tok = getattr(usage, "candidates_token_count", 0) or 0
            page_cost = _cost(in_tok, out_tok)
            _run_totals["input_tokens"] += in_tok
            _run_totals["output_tokens"] += out_tok
            _run_totals["cost_usd"] += page_cost
            _run_totals["pages"] += 1
            extracted["_usage"] = {"input_tokens": in_tok, "output_tokens": out_tok, "cost_usd": page_cost}
            return extracted

        except json.JSONDecodeError as e:
            print(f"    JSON parse error p{page_data['page_num']} attempt {attempt+1}: {e}")
        except Exception as e:
            print(f"    Gemini error p{page_data['page_num']} attempt {attempt+1}: {e}")

        if attempt < retry:
            time.sleep(3)

    # Fallback — empty stub so pipeline doesn't break
    return {
        "page_num": page_data["page_num"],
        "page_summary": "Extraction failed",
        "document_type": "unknown",
        "product_names": [],
        "extracted_text": "",
        "specifications": {},
        "key_facts": [],
        "diagram_labels": [],
        "warnings_notes": [],
        "extraction_failed": True,
    }


def process_pdf(pdf_path: str | Path, model, output_dir: str | Path,
                dpi: int = 200, sleep_between: float = 1.0) -> dict:
    """Full pipeline for one PDF. Returns the saved payload."""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nProcessing: {pdf_path.name}")
    pages = pdf_to_images(pdf_path, dpi=dpi)
    print(f"  {len(pages)} pages")

    chunks = []
    for i, page_data in enumerate(pages):
        print(f"  Extracting page {page_data['page_num']}/{len(pages)}...")
        chunk = extract_page_with_gemini(model, page_data)
        chunk["source_file"] = pdf_path.name
        chunks.append(chunk)

        u = chunk.get("_usage", {})
        if u:
            print(
                f"    tokens: in={u['input_tokens']:,} out={u['output_tokens']:,} "
                f"| page ${u['cost_usd']:.4f} "
                f"| run total: {_run_totals['pages']} pages, ${_run_totals['cost_usd']:.3f}"
            )

        if i < len(pages) - 1:
            time.sleep(sleep_between)

    failed_pages = [c["page_num"] for c in chunks if c.get("extraction_failed")]

    result = {
        "source_file": pdf_path.name,
        "total_pages": len(pages),
        "chunks": chunks,
        "metadata": {
            "dpi": dpi,
            "model": GEMINI_MODEL,
            "prompt_version": "1.0",
            "failed_pages": failed_pages,
        },
    }

    if failed_pages:
        print(f"  WARNING: extraction failed on pages {failed_pages}")

    output_file = output_dir / f"{pdf_path.stem}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  Saved -> {output_file}")
    return result


# ── CLI for single-file testing ──────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract structured content from a single PDF")
    parser.add_argument("--pdf", required=True, help="Path to a PDF file")
    parser.add_argument("--output", default="./knowledge_base")
    parser.add_argument("--dpi", type=int, default=200)
    args = parser.parse_args()

    model = setup_gemini()
    process_pdf(args.pdf, model, args.output, args.dpi)
