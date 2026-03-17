import nltk;

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

tokens = nltk.word_tokenize(text_content)
print(tokens)

tagged = nltk.pos_tag(tokens)
print(tagged[0:6])