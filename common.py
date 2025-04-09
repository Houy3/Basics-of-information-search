import os
from tqdm import tqdm
import pymorphy3
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
import re
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)
russian_stopwords = set(stopwords.words('russian'))
tokenizer = RegexpTokenizer(r'\b[а-яё]{2,}\b', flags=re.IGNORECASE)
morph = pymorphy3.MorphAnalyzer()

def lemmatize_tokens(tokens):
    lemmas = defaultdict(list)
    seen_in_lemmas = set()

    # Прогресс-бар для лемматизации
    for token in tqdm(tokens, desc="Лемматизация", unit="токен"):
        lemma = morph.parse(token)[0].normal_form
        lemma = lemma.replace("-", "")
        if token not in seen_in_lemmas:
            seen_in_lemmas.add(token)
            lemmas[lemma].append(token)
    return lemmas

def tokenize(text):
    return tokenizer.tokenize(text)

def clean_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = soup.get_text(separator=' ')
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'(?<!\s)-(?!\s)|^-\s|\s-$', ' ', cleaned_text)
    return cleaned_text.strip()

def process_files(file_name):
    tokens = set()
    with open(file_name, 'r', encoding='utf-8') as f:
        text = clean_html(f.read())

        # Прогресс-бар для токенизации
        for token in tqdm(tokenize(text), desc="Токенизация", unit="токен"):
            token = token.lower()
            if token not in russian_stopwords:
                tokens.add(token)
    return list(tokens)

# Основной цикл с прогресс-баром
article_list_folder = "../Work1/result/article_list"
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "result")

# Прогресс-бар для обработки файлов
files = [f for f in os.listdir(article_list_folder) if f.endswith('.txt')]
for file_name in tqdm(files, desc="Обработка файлов", unit="файл"):
    full_path = os.path.join(article_list_folder, file_name)

    # Обработка файла
    tokens = process_files(full_path)
    lemmas = lemmatize_tokens(tokens)

    # Сохранение результатов
    short_name = file_name.split('.')[0]
    with open(f"{OUTPUT_DIRECTORY}/{short_name}-tokens.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))

    with open(f"{OUTPUT_DIRECTORY}/{short_name}-lemmas.txt", "w", encoding="utf-8") as f:
        for lemma, words in lemmas.items():
            f.write(f"{lemma} {' '.join(words)}\n")