import os
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from collections import defaultdict
import pymorphy2
import nltk

nltk.download('stopwords')

morph = pymorphy2.MorphAnalyzer()
russian_stopwords = set(stopwords.words('russian'))

def clean_html(text):
    soup = BeautifulSoup(text, 'html.parser')
    cleaned_text = soup.get_text()
    cleaned_text = re.sub(r'\s-\s|^-\s|-$', ' ', cleaned_text)
    return cleaned_text

def tokenize(text):
    text = re.sub(r'[^а-яА-ЯёЁ\- ]', ' ', text.lower())
    tokens = text.split()
    return [
        t for t in tokens
        if t not in russian_stopwords
           and not re.search(r'\d', t)
           and t.strip() != '-'
    ]

def process_files(folder_path):
    seen_tokens = set()  # Для глобального удаления дубликатов
    all_tokens = []
    for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                text = clean_html(f.read())
                tokens = tokenize(text)
                for token in tokens:
                    if token not in seen_tokens:
                        seen_tokens.add(token)
                        all_tokens.append(token)
    return all_tokens

def lemmatize(tokens):
    lemmas = defaultdict(list)
    seen_in_lemmas = set()  # Для уникальности токенов внутри лемм
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        lemma = lemma.replace("-", "")
        if token not in seen_in_lemmas:
            seen_in_lemmas.add(token)
            lemmas[lemma].append(token)
    return lemmas

folder_path = "../Work1/result/article_list"
tokens = process_files(folder_path)
lemmas = lemmatize(tokens)

with open("tokens.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(tokens))

with open("lemmas.txt", "w", encoding="utf-8") as f:
    for lemma, words in lemmas.items():
        if len(words) > 1:
            f.write(f"{lemma} {' '.join(words)}\n")