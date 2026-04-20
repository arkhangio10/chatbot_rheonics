"""
LLM layer: calls Gemini 2.5 Flash with retrieved context.

The system prompt is loaded from docs/SYSTEM_PROMPT.md (single source of
truth). The retrieved context and user question are templated into the
user message.
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_ANSWER_MODEL = os.environ.get("GEMINI_ANSWER_MODEL", "gemini-2.5-flash")

# Project root = parent of the backend/ folder this file lives in.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYSTEM_PROMPT_PATH = PROJECT_ROOT / "docs" / "SYSTEM_PROMPT.md"

# Cached prompt parts (loaded once per process).
_PROMPT_CACHE: dict | None = None


def _ensure_gemini_configured():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=key)


def _parse_system_prompt_file() -> dict:
    """
    Parse docs/SYSTEM_PROMPT.md and return the prompt split into:
      - system_instruction: everything before the "## Context" section
      - user_template:      the "## Context\n{retrieved_chunks}\n## User question\n{user_query}" part

    The file contains one fenced code block under "## Current version".
    We extract that block, then split on the "## Context" heading.
    """
    text = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

    fence_match = re.search(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL)
    if not fence_match:
        raise ValueError(
            f"No fenced code block found in {SYSTEM_PROMPT_PATH}. "
            "The prompt must live inside a ``` ... ``` block."
        )
    prompt_body = fence_match.group(1).strip()

    split = re.split(r"^##\s+Context\s*$", prompt_body, maxsplit=1, flags=re.MULTILINE)
    if len(split) != 2:
        raise ValueError(
            "Prompt block must contain a '## Context' section separating "
            "the system instruction from the user template."
        )
    system_instruction = split[0].strip()
    user_template = "## Context\n" + split[1].strip()

    if "{retrieved_chunks}" not in user_template or "{user_query}" not in user_template:
        raise ValueError(
            "User template must contain both {retrieved_chunks} and "
            "{user_query} placeholders."
        )

    return {"system": system_instruction, "user_template": user_template}


def load_system_prompt() -> dict:
    """Return the cached prompt parts (loads on first call)."""
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        _PROMPT_CACHE = _parse_system_prompt_file()
    return _PROMPT_CACHE


def answer_question(question: str, context_block: str) -> dict:
    """Call Gemini with context + question, return structured response."""
    _ensure_gemini_configured()
    prompt = load_system_prompt()

    user_message = prompt["user_template"].format(
        retrieved_chunks=context_block,
        user_query=question,
    )

    model = genai.GenerativeModel(
        GEMINI_ANSWER_MODEL,
        system_instruction=prompt["system"],
    )
    response = model.generate_content(user_message)

    usage = getattr(response, "usage_metadata", None)
    return {
        "answer": response.text,
        "model": GEMINI_ANSWER_MODEL,
        "usage": {
            "input_tokens": getattr(usage, "prompt_token_count", None),
            "output_tokens": getattr(usage, "candidates_token_count", None),
        },
    }
