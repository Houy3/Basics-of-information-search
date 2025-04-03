import os
from nltk.corpus import stopwords
import nltk
from common import lemmatize_tokens, tokenize, clean_html

nltk.download('stopwords')
russian_stopwords = set(stopwords.words('russian'))

article_list_folder = "../Work1/result/article_list"
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "result") # Выходная папка

# читаем файл, чистим html теги и разбиваем на токены
def process_files(file_name):
    tokens = set()
    with open(file_name, 'r', encoding='utf-8') as f:
        for token in tokenize(clean_html(f.read())):
            token = token.lower()
            if token not in russian_stopwords:
                tokens.add(token)
    return list(tokens)

# main

for file_name in os.listdir(article_list_folder):

    tokens = process_files(os.path.join(article_list_folder, file_name))
    lemmas = lemmatize_tokens(tokens)

    short_file_name = file_name.split('.')[0]

    with open(os.path.join(OUTPUT_DIRECTORY, short_file_name + "-tokens.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))

    with open(os.path.join(OUTPUT_DIRECTORY, short_file_name + "-lemmas.txt"), "w", encoding="utf-8") as f:
        for lemma, words in lemmas.items():
            f.write(f"{lemma} {' '.join(words)}\n")
