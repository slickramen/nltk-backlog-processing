from rake_nltk import Rake
from nltk.corpus import stopwords

file_path = './samples/sample.txt'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
except FileNotFoundError:
    print(f"Error: The file '{file_path}' was not found.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    exit()


custom_stopwords = set(stopwords.words('english'))
custom_stopwords.update([
    "add", "fix", "implement", "create", "update",
    "need", "using", "use", "make", "task", "app"
])

r = Rake(stopwords=custom_stopwords)

r.extract_keywords_from_text(text_content)
keywords = r.get_ranked_phrases_with_scores()

def is_technical(phrase):
    tech_signals = [
        "api", "db", "database", "schema", "ui", "ux",
        "test", "auth", "sync", "middleware",
        "frontend", "backend", "service",
        "component", "state", "endpoint"
    ]
    
    return any(signal in phrase.lower() for signal in tech_signals)

filtered_keywords = [
    (score, kw) for score, kw in keywords if is_technical(kw)
]

for score, kw in filtered_keywords[:20]:
    print(f"{kw} ({score})")

