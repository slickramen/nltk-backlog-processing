"""
Task Categorisation Prototype
==============================
Categorises scrum backlog tasks by:
  1. Stack area       - frontend / backend / fullstack
  2. Implementation   - controller, service, repository, API, UI component, etc.
  3. Core concepts    - auth, CRUD, REST, state management, validation, etc.

Uses NLTK for tokenisation, stop-word removal, and stemming, then applies
keyword/pattern matching against curated taxonomy dictionaries.
"""

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# ---------------------------------------------------------------------------
# Download required NLTK data (safe to run multiple times)
# ---------------------------------------------------------------------------
for pkg in ("punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"):
    nltk.download(pkg, quiet=True)

# ---------------------------------------------------------------------------
# Stemmer
# ---------------------------------------------------------------------------

stemmer = PorterStemmer()

def stem_set(kws: set) -> set:
    """Stem a flat keyword set."""
    return {stemmer.stem(w) for w in kws}

def stem_keyword_dict(kws: dict | set) -> dict | set:
    """Stem keyword sets — handles both flat sets and strong/weak dicts."""
    if isinstance(kws, dict):
        return {key: stem_set(val) for key, val in kws.items()}
    return stem_set(kws)

# ---------------------------------------------------------------------------
# Taxonomy dictionaries  (defined in plain English, stemmed at startup)
# ---------------------------------------------------------------------------

_STACK_KEYWORDS_RAW = {
    "frontend": {
        "ui", "interface", "component", "button", "form", "modal", "page",
        "view", "template", "css", "style", "layout", "responsive", "display",
        "render", "react", "angular", "vue", "html", "dom", "client",
        "dashboard", "navbar", "sidebar", "popup", "toast", "table",
    },
    "backend": {
        "api", "endpoint", "controller", "service", "repository", "database",
        "db", "query", "server", "model", "schema", "migration", "route",
        "middleware", "authentication", "authorisation", "authorization",
        "jwt", "token", "password", "hash", "email", "schedule", "cron",
        "logic", "validation", "exception", "handler", "logging",
    },
}

_IMPLEMENTATION_KEYWORDS_RAW = {
    "controller":   {"controller", "route", "endpoint", "request", "response", "handler"},
    "service":      {"service", "logic", "business", "process", "calculate", "compute"},
    "repository":   {"repository", "repo", "dao", "database", "query", "crud", "persist", "store"},
    "api":          {"api", "rest", "endpoint", "http", "request", "response", "payload", "json"},
    "ui_component": {"component", "button", "form", "modal", "navbar", "sidebar", "table",
                     "input", "dropdown", "card", "page", "view", "layout", "widget"},
    "model":        {"model", "entity", "schema", "class", "object", "dto", "struct"},
    "migration":    {"migration", "migrate", "schema", "table", "column", "index", "seed"},
    "middleware":   {"middleware", "interceptor", "filter", "guard", "pipe"},
    "test":         {"test", "spec", "unit", "integration", "mock", "stub", "assert", "coverage"},
    "config":       {"config", "configuration", "environment", "env", "setting", "setup"},
}

_CONCEPT_KEYWORDS_RAW = {
    "authentication":   {"login", "logout", "signin", "signup", "authenticate", "auth",
                         "jwt", "session", "token", "oauth", "password", "credential"},
    "authorisation":    {"authorise", "authorize", "permission", "role", "access", "privilege",
                         "restrict", "guard", "policy", "acl"},
    "CRUD":             {"create", "read", "update", "delete", "add", "edit", "remove",
                         "list", "get", "post", "put", "patch"},
    "validation":       {"validate", "validation", "sanitise", "sanitize", "check",
                         "constraint", "rule", "format", "required", "error"},
    "state_management": {"state", "store", "redux", "context", "observable", "reactive",
                         "global", "local", "prop", "binding"},
    "data_persistence": {"save", "persist", "store", "database", "db", "cache",
                         "repository", "storage", "load"},
    "REST_API":         {"rest", "api", "http", "get", "post", "put", "patch", "delete",
                         "endpoint", "resource", "json", "payload", "status"},
    "error_handling":   {"error", "exception", "handle", "catch", "throw", "fault",
                         "fail", "fallback", "retry", "log"},
    "search_filter":    {"search", "filter", "sort", "query", "find", "lookup",
                         "paginate", "pagination"},
    "notifications":    {"notification", "notify", "alert", "toast", "remind", "send"},
    "file_handling":    {"file", "upload", "download", "attachment", "image", "media",
                         "export", "import", "pdf", "csv"},
    "testing": {
        "strong": {"unit", "integration", "e2e", "mock", "stub", "coverage", "assert",
                   "spec", "pytest", "xunit", "manual", "playwright"},
        "weak":   {"test", "testing", "verify", "check", "confirm"},
    },
    "security":         {"security", "secure", "encrypt", "decrypt", "hash", "ssl",
                         "tls", "xss", "csrf", "injection", "sanitise"},
    "performance":      {"performance", "optimise", "optimize", "cache", "lazy",
                         "load", "async", "concurrent", "speed", "efficient"},
}

# Stem all dictionaries once at startup
STACK_KEYWORDS          = {k: stem_set(v) for k, v in _STACK_KEYWORDS_RAW.items()}
IMPLEMENTATION_KEYWORDS = {k: stem_set(v) for k, v in _IMPLEMENTATION_KEYWORDS_RAW.items()}
CONCEPT_KEYWORDS        = {k: stem_keyword_dict(v) for k, v in _CONCEPT_KEYWORDS_RAW.items()}

# ---------------------------------------------------------------------------
# NLP helpers
# ---------------------------------------------------------------------------

_stop_words = set(stopwords.words("english"))

# Stem domain noise too so it matches stemmed tokens
DOMAIN_NOISE = {
    stemmer.stem(w) for w in {
        "message", "format", "display", "show", "get", "given",
        "add", "fix", "make", "use", "need", "want", "relevant",
        "existing", "correct", "current", "new", "old",
    }
}

def preprocess(text: str) -> list[str]:
    """Lowercase → tokenise → stem → remove stop-words & domain noise."""
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if re.match(r"[a-z]", t)]
    tokens = [stemmer.stem(t) for t in tokens]          # stem before filtering
    tokens = [t for t in tokens
              if t not in _stop_words
              and t not in DOMAIN_NOISE]
    return tokens


def _score_category(tokens: list[str], token_set: set | dict, raw_text: str) -> float:
    """Handles both flat sets and strong/weak dicts."""
    if isinstance(token_set, dict):
        strong_hits = sum(1 for t in tokens if t in token_set["strong"])
        weak_hits   = sum(1 for t in tokens if t in token_set["weak"])
        return strong_hits * 2 + weak_hits

    score = sum(1 for t in tokens if t in token_set)
    raw_lower = raw_text.lower()
    for kw in token_set:
        if " " in kw and kw in raw_lower:
            score += 0.5
    return score


# ---------------------------------------------------------------------------
# Core categorisation logic
# ---------------------------------------------------------------------------

EXPLICIT_STACK_PATTERNS = [
    (r"\bfrontend\s+and\s+backend\b", "fullstack"),
    (r"\bbackend\s+and\s+frontend\b", "fullstack"),
    (r"\bfull[\s\-]?stack\b",         "fullstack"),
    (r"\bfrontend\b",                  "frontend"),
    (r"\bbackend\b",                   "backend"),
]

def detect_explicit_stack(text: str) -> str | None:
    """Returns a stack area if explicitly declared, else None."""
    for pattern, stack in EXPLICIT_STACK_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return stack
    return None

def categorise_stack(tokens: list[str], raw: str) -> dict:
    explicit = detect_explicit_stack(raw)
    if explicit:
        return {"stack_area": explicit, "source": "explicit"}

    fe = _score_category(tokens, STACK_KEYWORDS["frontend"], raw)
    be = _score_category(tokens, STACK_KEYWORDS["backend"], raw)

    if fe == 0 and be == 0:
        area = "unknown"
    elif fe > 0 and be > 0:
        area = "fullstack"
    else:
        area = "frontend" if fe > be else "backend"

    return {"stack_area": area, "source": "inferred"}


def categorise_implementation(tokens: list[str], raw: str) -> list[str]:
    scores = {
        impl: _score_category(tokens, kws, raw)
        for impl, kws in IMPLEMENTATION_KEYWORDS.items()
    }
    detected = sorted(
        [(impl, s) for impl, s in scores.items() if s > 0],
        key=lambda x: x[1], reverse=True,
    )
    return [impl for impl, _ in detected]


def categorise_concepts(tokens: list[str], raw: str) -> list[str]:
    scores = {}
    for concept, kws in CONCEPT_KEYWORDS.items():
        score = _score_category(tokens, kws, raw)

        if isinstance(kws, dict):
            has_strong = any(t in kws["strong"] for t in tokens)
            if not has_strong:
                continue

        if score >= 1:
            scores[concept] = score

    return [c for c, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


def clean_text(text: str) -> str:
    text = re.sub(r"\bac[\s\-]?\d+[:,]?\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"[-•*]+\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def categorise_task(title: str, description: str = "") -> dict:
    combined = clean_text(f"{title} {description}".strip())
    tokens = preprocess(combined)

    stack = categorise_stack(tokens, combined)
    implementations = categorise_implementation(tokens, combined)
    concepts = categorise_concepts(tokens, combined)

    return {
        "title": title,
        "stack_area": stack["stack_area"],
        "stack_source": stack["source"],
        "implementation_types": implementations,
        "core_concepts": concepts,
        "tokens_used": tokens,
    }


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_result(result: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Task : {result['title']}")
    print(f"{'=' * 60}")
    print(f"  Stack area            : {result['stack_area']} ({result['stack_source']})")
    print(f"  Implementation types  : {', '.join(result['implementation_types']) or 'none detected'}")
    print(f"  Core concepts         : {', '.join(result['core_concepts']) or 'none detected'}")
    print(f"  Tokens (debug)        : {result['tokens_used']}")


# ---------------------------------------------------------------------------
# Sample tasks
# ---------------------------------------------------------------------------

SAMPLE_TASKS = [
    (
        "As a user I can log into the application",
        "Implement a login page with email/password form. "
        "Validate credentials against the database. "
        "Return a JWT token on success and handle authentication errors.",
    ),
    (
        "Create an API endpoint to list all tasks in a project",
        "Build a REST GET endpoint at /api/projects/{id}/tasks. "
        "The controller should call the task service which fetches from the repository. "
        "Support filtering by status and pagination.",
    ),
    (
        "Build a dashboard page showing sprint progress",
        "Create a React component that displays a burndown chart and task counts. "
        "Fetch data from the existing API. "
        "Use responsive CSS layout so it works on mobile.",
    ),
    (
        "Add file upload support for task attachments",
        "Allow users to upload files to a task. "
        "Store files securely on the server and save metadata to the database. "
        "Validate file type and size. "
        "Display uploaded attachments in the task detail view.",
    ),
    (
        "Write unit tests for the user service",
        "Add unit test coverage for UserService. "
        "Mock the repository layer and assert business logic behaves correctly. "
        "Cover edge cases for validation and error handling.",
    ),
    (
        "3 - Add Edit Validation (Backend and Frontend)",
        "Relevant AC's - AC3, AC4, AC5, AC6, AC7"
        "- Add all 'Create Task' validation to Editing Task."
        "- Conduct Frontend and Backend testing",
    ),
    (
        "AC2: Error message wrong format",
        """PROBLEM: Given email being
😍😍😍😍😍😍@myemail.com we aren't getting correct error message. Getting "Invalid email or password" instead.

Fix which error message is displayed.
Relevant AC's
- AC3, AC4, AC5, AC6, AC7

- Add all "Create Task" validation to Editing Task.
- Conduct Frontend and Backend testing
"""
    ),
    (
        "The password reset via email API",
        "manual testing if password is correct, testing if password is correct "
        "Implement the existing API from .Net identity library"
    ),
]

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    for title, description in SAMPLE_TASKS:
        result = categorise_task(title, description)
        print_result(result)
    print(f"\n{'=' * 60}\n")