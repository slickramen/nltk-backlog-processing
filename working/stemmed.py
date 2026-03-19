"""
Tasks are categories by
1. Stack area     - frontend / backend / fullstack
2. Implementation - controller, service, repository, api, etc.
3. Core concepts  - auth, CRUD, REST, validation, etc.

Uses NLTK for tokenisation, stop-word removal, and stemming, then applies
keyword/pattern matching against curated taxonomy dictionaries.

General processing flow:
Given a task t and a desired output o, where o is in the format:
{
    task_title,
    task_techstack,
    task_implementation_areas,
    task_implementation_concepts
}

Run the following procedure to derive o from t:
1. Preprocess and clean up the input. This involves getting rid of unnecessary characters
    or symbols that may confuse the tokeniser. The preprocessing step also converts the text
    to lowercase, tokenises it and then stems it to its root form (such as running and runs -> run).
2. Filter out domain noise and stop words to cleanup input further (get rid of useless jargon)
3. Categorise the tech stack based on the raw data and tokens
4. Categorise the implementation areas based on the raw data and tokens
5. Categorise the implementation concepts based on the raw data and tokens
6. Print output
"""

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

from py.sample import SAMPLE_TASKS
from py.language_dict import PLAIN_CONCEPT_KEYWORDS, PLAIN_IMPLEMENTATION_KEYWORDS, PLAIN_STACK_KEYWORDS

# download nltk data
for pkg in ("punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"):
    nltk.download(pkg, quiet=True)

# steps
stemmer = PorterStemmer()

# stem a set of keywords
def stem_set(words):
    return {stemmer.stem(w) for w in words}

# stem a dict of keywords, used for nested keyword sets
def stem_keyword_dict(words):
    if isinstance(words, dict):
        return {key: stem_set(val) for key, val in words.items()}
    
    return stem_set(words)

# stem dictionaries
STACK_KEYWORDS = {k: stem_set(v) for k, v in PLAIN_STACK_KEYWORDS.items()}
IMPLEMENTATION_KEYWORDS = {k: stem_set(v) for k, v in PLAIN_IMPLEMENTATION_KEYWORDS.items()}
CONCEPT_KEYWORDS = {k: stem_keyword_dict(v) for k, v in PLAIN_CONCEPT_KEYWORDS.items()}

# list of stop words
stop_words = set(stopwords.words("english"))

# stemmed domain noise (irrelevant language)
DOMAIN_NOISE = {
    stemmer.stem(w) for w in {
        "message", "format", "display", "show", "get", "given",
        "add", "fix", "make", "use", "need", "want", "relevant",
        "existing", "correct", "current", "new", "old",
    }
}

# preprocess text to make result cleaner
# 1. convert to lowercase and tokenise input
# 2. stem tokens
# 3. filter out stop words and domain noise
def preprocess(text):
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if re.match(r"[a-z]", t)]
    tokens = [stemmer.stem(t) for t in tokens]
    tokens = [t for t in tokens
              if t not in stop_words
              and t not in DOMAIN_NOISE]
    
    return tokens

# score a given category
def score_category(tokens, token_set, raw_text):
    # strong and weak dicts, strong words are prioritised
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

# categorising patterns of the tech stack
EXPLICIT_STACK_PATTERNS = [
    (r"\bfrontend\s+and\s+backend\b", "fullstack"),
    (r"\bbackend\s+and\s+frontend\b", "fullstack"),
    (r"\bfull[\s\-]?stack\b",         "fullstack"),
    (r"\bfrontend\b",                  "frontend"),
    (r"\bbackend\b",                   "backend"),
]

# determine whether techstack is explicitly stated in message
def detect_explicit_stack(text):
    for pattern, stack in EXPLICIT_STACK_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return stack
    
    return None

# categorise task techstack (may be explicit or inferred)
def categorise_stack(tokens, raw):
    explicit = detect_explicit_stack(raw)

    if explicit:
        return {"stack_area": explicit, "source": "explicit"}

    fe = score_category(tokens, STACK_KEYWORDS["frontend"], raw)
    be = score_category(tokens, STACK_KEYWORDS["backend"], raw)

    if fe == 0 and be == 0:
        area = "unknown"
    elif fe > 0 and be > 0:
        area = "fullstack"
    else:
        area = "frontend" if fe > be else "backend"

    return {"stack_area": area, "source": "inferred"}

# categorise task implementation
def categorise_implementation(tokens, raw):
    scores = {
        impl: score_category(tokens, kws, raw) for impl, kws in IMPLEMENTATION_KEYWORDS.items()
    }

    detected = sorted(
        [(impl, s) for impl, s in scores.items() if s > 0], key=lambda x: x[1], reverse=True,
    )

    return [impl for impl, _ in detected]

# categorise task concepts
def categorise_concepts(tokens, raw):
    scores = {}
    for concept, kws in CONCEPT_KEYWORDS.items():
        score = score_category(tokens, kws, raw)

        if isinstance(kws, dict):
            has_strong = any(t in kws["strong"] for t in tokens)
            if not has_strong:
                continue

        if score >= 1:
            scores[concept] = score

    return [c for c, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

# clean up noise in message
def clean_text(text):
    text = re.sub(r"\bac[\s\-]?\d+[:,]?\b", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"[-•*]+\s*", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# categorise a task
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

# printer
def print_result(result: dict) -> None:
    task_title = result['title']
    stack_area = f"{result['stack_area']} ({result['stack_source']})"
    implementation_types = ', '.join(result['implementation_types']) or 'none detected'
    implementation_concepts = ', '.join(result['core_concepts']) or 'none detected'

    print(f"\n{'=' * 60}")
    print(f"Task: '{task_title}'")
    print(f"- Stack area:              {stack_area}")
    print(f"- Implementation types:    {implementation_types}")
    print(f"- Implementation concepts: {implementation_concepts}")
    # print(f"- Tokens (debug)        : {result['tokens_used']}")


if __name__ == "__main__":
    for title, description in SAMPLE_TASKS:
        result = categorise_task(title, description)
        print_result(result)
    print(f"\n{'=' * 60}\n")