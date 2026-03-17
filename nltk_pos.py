from nltk import word_tokenize, pos_tag
from rake_nltk import Rake
from nltk.corpus import stopwords

file_path = './samples/sample.txt'

# stopwords - will be ommitted
STOPWORDS = [
    "add", "fix", "implement", "create", "update", "need", "using", "use", "make", 
    "task", "app"
]

# technical phrases - will be prioritised
TECHNICAL_PHRASES = [
    "api", "database", "ui", "test", "auth", "service", "component", "state", 
    "endpoint", "frontend", "backend", "controller", "repository", "bug", 
    "issue", "exception", "error", "validation"
]

# read file
with open(file_path, 'r', encoding='utf-8') as f:
    text_content = f.read()

# add custom stopwords
custom_stopwords = set(stopwords.words('english'))
custom_stopwords.update(STOPWORDS)

# rake - Rapid Automatic Keyword Extraction
r = Rake(stopwords=custom_stopwords)

# extract nouns from a message
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

# combine nouns
noun_phrases = extract_noun_phrases(text_content)
joined_phrases = ". ".join(noun_phrases)

# rake them!
r.extract_keywords_from_text(joined_phrases)
keywords = r.get_ranked_phrases_with_scores()

# check if a phrase is in technical phrases list
def is_technical(phrase):
    return any(word in phrase.lower() for word in TECHNICAL_PHRASES)

# top keywords
print("\nTop Keywords:\n")
for score, kw in keywords[:20]:
    print(f"{kw} ({score:.2f})")

seen = set()
final_keywords = []

for score, kw in keywords:
    kw = kw.replace("_", " ").lower()
    
    if kw not in seen and is_technical(kw):
        seen.add(kw)
        final_keywords.append((score, kw))

# top filtered keywords
print("\nTop (Filtered) Keywords:\n")
for score, kw in final_keywords[:20]:
    print(f"{kw} ({score:.2f})")
