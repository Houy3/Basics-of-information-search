import os
from nltk.corpus import stopwords
import nltk
from common import lemmatize_tokens, tokenize, clean_html

nltk.download('stopwords')
russian_stopwords = set(stopwords.words('russian'))

article_list_folder = "../Work1/result/article_list"
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "result") # Выходная папка

# читаем файл, чистим html теги и разбиваем на токены
def process_files(folder_path):
    tokens = set()
    for filename in os.listdir(folder_path):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
            for token in tokenize(clean_html(f.read())):
                token = token.lower()
                if token not in russian_stopwords:
                    tokens.add(token)
    return list(tokens)

# main
tokens = process_files(article_list_folder)
lemmas = lemmatize_tokens(tokens)

with open(os.path.join(OUTPUT_DIRECTORY, "tokens.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(tokens))

with open(os.path.join(OUTPUT_DIRECTORY, "lemmas.txt"), "w", encoding="utf-8") as f:
    for lemma, words in lemmas.items():
        f.write(f"{lemma} {' '.join(words)}\n")
