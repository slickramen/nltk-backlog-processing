"""
Tasks are categorised by:
1. Stack area     - frontend / backend / fullstack
2. Implementation - controller, service, repository, api, etc.
3. Core concepts  - auth, CRUD, REST, validation, etc.

Preprocessing is limited to text cleaning. Classification is fully delegated
to a local model via Ollama's chat endpoint with native JSON mode.
"""

import json
import re
import requests

from .language_dict import (
    PLAIN_CONCEPT_KEYWORDS,
    PLAIN_IMPLEMENTATION_KEYWORDS,
)
from .sample import SAMPLE_TASKS

# ── Ollama config ─────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:latest"

# ── Taxonomy ──────────────────────────────────────────────────────────────────

VALID_STACKS = ["frontend", "backend", "fullstack", "unknown"]
VALID_IMPLEMENTATIONS = list(PLAIN_IMPLEMENTATION_KEYWORDS.keys())
VALID_CONCEPTS = list(PLAIN_CONCEPT_KEYWORDS.keys())

# ── System prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = f"""You are a senior software engineer classifying scrum backlog items.
Given a task title and optional description, return a JSON object classifying the task.

Rules:
- Only use values from the provided taxonomy lists — never invent new ones
- Choose all implementation types and concepts that genuinely apply
- If nothing applies, use an empty list
- stack_source must be "explicit" if the stack was directly stated in the text, otherwise "inferred"

Taxonomy:
  valid implementation types: {json.dumps(VALID_IMPLEMENTATIONS)}
  valid core concepts: {json.dumps(VALID_CONCEPTS)}

Infer the stack from context. Use these rules as a guide:
- "backend" if the task involves APIs, endpoints, server logic, databases, or authentication
- "frontend" if it involves UI, components, pages, or styling
- "fullstack" if it clearly spans both layers
- "unknown" only if there is genuinely no signal

Return exactly this structure:
{{
  "stack_layer": "<one of: frontend, backend, fullstack, unknown>",
  "stack_source": "<explicit|inferred>",
  "implementation_types": ["<type>"],
  "core_concepts": ["<concept>"]
}}"""

# ── Text cleaning ─────────────────────────────────────────────────────────────


def clean_text(text: str) -> str:
    """Strip ticket prefixes, bullet characters, non-ASCII, and extra whitespace."""
    text = re.sub(r"\bac[\s\-]?\d+[:,]?\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"[-•*]+\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── LLM classification ────────────────────────────────────────────────────────


def build_user_message(title: str, description: str) -> str:
    parts = [f"Title: {title}"]
    if description:
        parts.append(f"Description: {description}")
    return "\n".join(parts)


def query_ollama(user_message: str) -> dict:
    """Send a chat request to Ollama with JSON mode enabled."""
    payload = {
        "model": MODEL,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.05, "seed": 42},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    }
    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return json.loads(response.json()["message"]["content"])


def validate_and_sanitise(data: dict) -> dict:
    """Ensure LLM output only contains values from our taxonomy."""
    stack = data.get("stack_layer", "unknown").lower().strip()
    if stack not in VALID_STACKS:
        stack = "unknown"

    return {
        "stack_layer": stack,
        "stack_source": data.get("stack_source", "inferred"),
        "implementation_types": [
            i
            for i in data.get("implementation_types", [])
            if i in VALID_IMPLEMENTATIONS
        ],
        "core_concepts": [
            c for c in data.get("core_concepts", []) if c in VALID_CONCEPTS
        ],
    }


def categorise_task(title: str, description: str = "") -> dict:
    title = clean_text(title)
    description = clean_text(description)

    try:
        data = query_ollama(build_user_message(title, description))
        classified = validate_and_sanitise(data)
    except (ValueError, json.JSONDecodeError, requests.RequestException) as e:
        print(f"Classification failed for '{title}': {e}")
        classified = {
            "stack_layer": "unknown",
            "stack_source": "error",
            "implementation_types": [],
            "core_concepts": [],
        }

    return {"title": title, "description": description, **classified}


# ── Printer ───────────────────────────────────────────────────────────────────


def print_result(result: dict) -> None:
    print(f"Task: '{result['title']}'")
    print(
        f"- Stack layer:             {result['stack_layer']} ({result['stack_source']})"
    )
    print(
        f"- Implementation types:    {', '.join(result['implementation_types']) or 'none detected'}"
    )
    print(
        f"- Core concepts:           {', '.join(result['core_concepts']) or 'none detected'}"
    )
    print("")


if __name__ == "__main__":
    for title, description in SAMPLE_TASKS:
        result = categorise_task(title, description)
        print_result(result)
