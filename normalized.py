from nltk import word_tokenize, pos_tag
from rake_nltk import Rake
from nltk.corpus import stopwords
from collections import Counter
from collections import defaultdict

file_path = './samples/sample.txt'

# stopwords - will be omitted
STOPWORDS = [
    "add", "fix", "implement", "create", "update",
    "optimize", "improve", "refactor", "design",
    "integrate", "remove", "correct", "enhance"
]

# technical phrases - prioritised / boosted
TECHNICAL_PHRASES = [
    "api", "database", "ui", "test", "auth", "service",
    "component", "state", "endpoint"
    "controller", "repository", "bug", "issue", "exception",
    "error", "validation", "refactor", "schema", "queries", "coverage", "middleware"
]

# --- classification keywords ---
BUG_WORDS = ["bug", "fix", "error", "issue", "crash", "exception"]
TECH_WORDS = TECHNICAL_PHRASES
FEATURE_WORDS = ["feature", "add", "support", "enable", "allow"]

# --- read file ---
with open(file_path, 'r', encoding='utf-8') as f:
    text_content = f.read()

# --- stopwords ---
custom_stopwords = set(stopwords.words('english'))
custom_stopwords.update(STOPWORDS)

# --- rake ---
r = Rake(stopwords=custom_stopwords)

# --- extract noun phrases ---
def extract_noun_phrases(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    
    noun_phrases = []
    current = []
    
    for word, tag in tagged:
        if tag.startswith("NN") or tag.startswith("JJ"):
            current.append(word)
        else:
            if current:
                noun_phrases.append(" ".join(current))
                current = []
    
    if current:
        noun_phrases.append(" ".join(current))
    
    return noun_phrases

noun_phrases = extract_noun_phrases(text_content)

# --- frequency (for boosting repeated concepts) ---
freq = Counter([np.lower() for np in noun_phrases])

# --- rake scoring ---
r.extract_keywords_from_sentences(noun_phrases)
keywords = r.get_ranked_phrases_with_scores()

# --- classification ---
def classify(phrase):
    phrase = phrase.lower()
    
    if any(word in phrase for word in BUG_WORDS):
        return "bug"
    elif any(word in phrase for word in TECH_WORDS):
        return "tech"
    elif any(word in phrase for word in FEATURE_WORDS):
        return "feature"
    else:
        return "other"

# --- domain boosting ---
def boost_score(score, phrase):
    phrase_lower = phrase.lower()
    
    # boost if contains technical phrase
    if any(word in phrase_lower for word in TECHNICAL_PHRASES):
        score += 3
    
    # boost if frequent
    score += freq.get(phrase_lower, 0)
    
    return score

# --- clean + dedupe + classify ---
seen = set()
final_keywords = []

for score, kw in keywords:
    kw_clean = kw.replace("_", " ").lower()
    
    if kw_clean in seen:
        continue
    
    seen.add(kw_clean)
    
    boosted_score = boost_score(score, kw_clean)
    category = classify(kw_clean)
    
    final_keywords.append((boosted_score, kw_clean, category))

# --- sort by boosted score ---
final_keywords.sort(reverse=True, key=lambda x: x[0])

# --- output ---
print("\nTop Keywords (Ranked + Classified):\n")

for score, kw, category in final_keywords[:30]:
    print(f"{kw:40} | {category:8} | {score:.2f}")

LAYERS = ["frontend", "backend"]
COMPONENTS = [
    "api", "service", "controller", "repository",
    "schema", "database", "ui", "page",
    "middleware", "tests", "coverage"
]

def extract_core_concept(phrase):
    words = phrase.lower().split()
    
    # remove action/stop words
    filtered = [w for w in words if w not in STOPWORDS]
    
    # detect layer
    layer = next((w for w in filtered if w in LAYERS), None)
    
    # detect components
    components = [w for w in filtered if w in TECHNICAL_PHRASES]
    
    # layer + component combo
    if layer and components:
        return f"{layer} {components[0]}"
    
    # 2-word technical combo
    if len(components) >= 2:
        return " ".join(components[:2])
    
    # single component, but only if meaningful
    if len(components) == 1:
        return components[0]
    
    # fallback: take filtered phrase if 2+ words (keeps domain context)
    if len(filtered) >= 2:
        return " ".join(filtered[:2])
    
    return None

concept_scores = defaultdict(float)
concept_counts = defaultdict(int)

for score, kw, category in final_keywords:
    concept = extract_core_concept(kw)
    
    if concept:
        concept_scores[concept] += score
        concept_counts[concept] += 1


concept_list = []

for concept in concept_scores:
    total_score = concept_scores[concept]
    count = concept_counts[concept]
    
    # combine score + frequency
    final_score = total_score + count * 2
    
    concept_list.append((final_score, concept, count))

concept_list.sort(reverse=True)

print("\nBoiled Down Concepts:\n")

for score, concept, count in concept_list[:20]:
    print(f"{concept:25} | mentions: {count} | score: {score:.2f}")