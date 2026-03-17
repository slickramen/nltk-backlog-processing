LAYERS = ["frontend", "backend"]
COMPONENTS = [
    "api", "service", "controller", "repository",
    "schema", "database", "ui", "page", "form",
    "middleware", "tests", "coverage", "endpoint"
]

ACTION_WORDS = [
    "add", "fix", "implement", "create", "update",
    "optimize", "improve", "refactor", "design",
    "integrate", "remove", "correct", "enhance",
    "complete", "remove", "handle", "support"
]

STOPWORDS = [
    "task", "issue", "user", "item", "items", "feature"
]

from nltk import word_tokenize, pos_tag

def extract_relevant_words(text):
    tokens = word_tokenize(text.lower())
    tagged = pos_tag(tokens)
    # only nouns/adjectives, remove action/stop words
    return [
        w for w, tag in tagged 
        if (tag.startswith("NN") or tag.startswith("JJ")) 
        and w not in STOPWORDS 
        and w not in ACTION_WORDS
    ]

def map_to_concepts(words):
    concepts = set()
    
    layer = next((w for w in words if w in LAYERS), None)
    components_found = [w for w in words if w in COMPONENTS]
    
    # Case 1: layer + component
    if layer and components_found:
        for comp in components_found:
            concepts.add(f"{layer} {comp}")
    
    # Case 2: multiple components without layer
    if len(components_found) >= 2:
        for i in range(len(components_found)-1):
            concepts.add(f"{components_found[i]} {components_found[i+1]}")
    
    # Case 3: single component
    for comp in components_found:
        concepts.add(comp)
    
    return list(concepts)

def extract_task_concepts(title, description):
    text = f"{title}. {description}"
    words = extract_relevant_words(text)
    concepts = map_to_concepts(words)
    return concepts

title = [
    "Optimize backend API endpoints",
    "3 - Add Edit Validation (Backend and Frontend)",
    "AC2: Error message wrong format",
    "Task 2 : The password reset via email API",
]
description = [
    "Refactor service layer to reduce latency and fix errors in controller",
    
    """Relevant AC's
- AC3, AC4, AC5, AC6, AC7

- Add all "Create Task" validation to Editing Task.
- Conduct Frontend and Backend testing
""",
"""
PROBLEM: Given email being 
😍😍😍😍😍😍@myemail.com we aren't getting correct error message. Getting "Invalid email or password" instead.

Fix which error message is displayed.
""",
"""
Implement the existing API from .Net identity library
"""
]


for i in range(len(title)):
    concepts = extract_task_concepts(title[i], description[i])
    print(concepts)
