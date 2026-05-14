# Scrum Backlog Classifier — Local LLM Setup

Classifies backlog items using a local Llama model via **Ollama**.
Extracts: concept category, stack, implementation areas, and implementation type.

---

## 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: download from https://ollama.com/download
```

## 2. Pull a Llama model

```bash
# Recommended: fast and capable (2GB)
ollama pull llama3.2

# Lighter option for low-RAM machines (1.3GB)
ollama pull llama3.2:1b

# More powerful if you have >=16GB RAM (5GB)
ollama pull llama3.1:8b
```

## 3. Start the Ollama server

```bash
ollama serve
# Runs at http://localhost:11434 by default
```

## 4. Install Python dependencies

```bash
pip install requests
```

## 5. Run the classifier

```bash
python backlog_processor.py
```

---

## Customising your taxonomy

Edit these lists at the top of `backlog_processor.py`:

| Variable               | What it controls                                             |
| ---------------------- | ------------------------------------------------------------ |
| `CONCEPT_CATEGORIES`   | High-level concepts / epics to classify into                 |
| `STACK_OPTIONS`        | frontend / backend / full stack (or extend with mobile etc.) |
| `IMPLEMENTATION_AREAS` | Technical areas: database, API, UI component, etc.           |
| `IMPLEMENTATION_TYPES` | new feature, bug fix, refactor, spike, etc.                  |
| `MODEL`                | Which Ollama model to use                                    |

---

## Using the classifier in your own code

```python
from backlog_processor import classify_item, classify_batch

# Single item
result = classify_item(
    title="Add pagination to the user list",
    description="The user table currently loads all rows, causing slow page load."
)
print(result.category)             # e.g. "UI / UX"
print(result.stack)                # e.g. "full stack"
print(result.implementation_areas) # e.g. ["UI component", "API"]
print(result.implementation_type)  # e.g. "enhancement"

# Batch of items
items = [
    {"title": "Fix login bug"},
    {"title": "Set up Redis caching", "description": "Cache API responses."},
]
results = classify_batch(items)
```

---

## Output format

Each classified item returns:

```json
{
	"title": "Add OAuth2 login with Google",
	"category": "Authentication & Authorisation",
	"stack": "full stack",
	"implementation_areas": ["API", "third-party integration"],
	"implementation_type": "new feature",
	"confidence_notes": ""
}
```

---

## Tips

- **Temperature is set to 0.1** for consistent, deterministic output. Increase it slightly if you want more varied results.
- If the model returns malformed JSON, the script logs a warning and falls back gracefully — it won't crash your batch run.
- For large backlogs, consider adding a small `time.sleep(0.5)` between items to avoid overwhelming Ollama.
- The `confidence_notes` field will be populated when the model finds an item ambiguous — useful for human review.
