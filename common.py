import pymorphy2
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
import re

tokenizer = RegexpTokenizer(r'\b[а-яё]{2,}\b', flags=re.IGNORECASE)
morph = pymorphy2.MorphAnalyzer()

def lemmatize_tokens(tokens):
    lemmas = defaultdict(list)
    seen_in_lemmas = set()
    for token in tokens:
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

def read_file_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def contains(string, sequence):
    return bool(re.search(sequence, string, re.IGNORECASE))