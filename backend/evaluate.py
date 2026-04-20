"""
Retrieval + answer evaluator for the Rheonics chatbot.

Parses docs/TEST_QUESTIONS.md, runs each question through the retriever,
and checks whether expected key facts appear in the top-k chunks. With
--answer it also runs the LLM and checks the final answer.

Usage:
    python -m backend.evaluate                    # retrieval only, k=5
    python -m backend.evaluate --k 8
    python -m backend.evaluate --answer           # also run the LLM
    python -m backend.evaluate --question 1 3 5   # subset by row number
"""

import re
import argparse
from pathlib import Path

from backend.retriever import retrieve, format_chunks_for_prompt
from backend.llm import answer_question


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_QUESTIONS_PATH = PROJECT_ROOT / "docs" / "TEST_QUESTIONS.md"


# ── Parsing ──────────────────────────────────────────────────────────────────

# Pull the first word/token out of a bullet-list or comma-separated expected
# answer. We split on commas and slashes to get multiple candidate key facts.
_SPLIT_RE = re.compile(r"[,/]")
# Strip markdown emphasis, trailing notes in parens, and the "Yes, " / "No, " lead-in.
_CLEAN_RE = re.compile(r"^(yes|no)[,:\s]+", flags=re.IGNORECASE)


def _clean(s: str) -> str:
    s = s.strip().strip("`*_").strip()
    s = _CLEAN_RE.sub("", s)
    return s.strip()


def parse_test_questions(path: Path = TEST_QUESTIONS_PATH) -> list[dict]:
    """Extract rows from every markdown table in TEST_QUESTIONS.md.

    Each row becomes: {"idx": int, "question": str, "expected": str,
                        "key_facts": [str, ...]}
    Rows without a numeric index column are skipped.
    """
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("|-") or line.startswith("|--"):
            continue

        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        if not cells[0].isdigit():
            continue  # header row or separator

        idx = int(cells[0])
        question = cells[1]
        expected = cells[2]

        # Extract candidate key facts: split on comma/slash, clean each.
        facts = [_clean(p) for p in _SPLIT_RE.split(expected)]
        facts = [f for f in facts if len(f) >= 2]

        rows.append({
            "idx": idx,
            "question": question,
            "expected": expected,
            "key_facts": facts,
        })
    return rows


# ── Scoring ──────────────────────────────────────────────────────────────────

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s).lower()


def score_retrieval(row: dict, chunks: list[dict]) -> dict:
    """A row passes retrieval if ANY of its key facts appears (case-insensitive,
    whitespace-normalized) in any of the top-k chunk texts."""
    haystack = _normalize(" ".join(c["text"] for c in chunks))
    hits = [f for f in row["key_facts"] if _normalize(f) in haystack]
    return {
        "passed": bool(hits),
        "hits": hits,
        "sources": [
            f"{c['metadata'].get('source', '?')} p{c['metadata'].get('page', '?')}"
            for c in chunks
        ],
    }


def score_answer(row: dict, answer: str) -> dict:
    haystack = _normalize(answer)
    hits = [f for f in row["key_facts"] if _normalize(f) in haystack]
    return {"passed": bool(hits), "hits": hits}


# ── Runner ───────────────────────────────────────────────────────────────────

def run(k: int = 5, also_answer: bool = False, subset: list[int] | None = None):
    rows = parse_test_questions()
    if subset:
        rows = [r for r in rows if r["idx"] in set(subset)]

    if not rows:
        print("No test questions parsed. Check docs/TEST_QUESTIONS.md format.")
        return

    print(f"Evaluating {len(rows)} question(s), k={k}"
          + (" + LLM" if also_answer else " (retrieval only)"))
    print("=" * 80)

    retrieval_passes = 0
    answer_passes = 0

    for row in rows:
        print(f"\n[{row['idx']:>2}] {row['question']}")
        print(f"     expected: {row['expected']}")

        chunks = retrieve(row["question"], k=k)
        r = score_retrieval(row, chunks)
        flag = "PASS" if r["passed"] else "FAIL"
        retrieval_passes += int(r["passed"])

        print(f"     retrieval: {flag}  hits={r['hits'] or '-'}")
        for s in r["sources"][:3]:
            print(f"        - {s}")

        if also_answer:
            if not chunks:
                print("     answer:    SKIP (no chunks)")
                continue
            result = answer_question(row["question"], format_chunks_for_prompt(chunks))
            a = score_answer(row, result["answer"])
            answer_passes += int(a["passed"])
            a_flag = "PASS" if a["passed"] else "FAIL"
            preview = result["answer"].replace("\n", " ")[:160]
            print(f"     answer:    {a_flag}  hits={a['hits'] or '-'}")
            print(f"        > {preview}")

    print("\n" + "=" * 80)
    total = len(rows)
    print(f"Retrieval: {retrieval_passes}/{total} "
          f"({retrieval_passes / total * 100:.0f}%)")
    if also_answer:
        print(f"Answers:   {answer_passes}/{total} "
              f"({answer_passes / total * 100:.0f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieval + answer evaluator")
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--answer", action="store_true",
                       help="Also call the LLM and score answers")
    parser.add_argument("--question", type=int, nargs="*",
                       help="Only run these question indices")
    args = parser.parse_args()
    run(k=args.k, also_answer=args.answer, subset=args.question)
