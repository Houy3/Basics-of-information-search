import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from collections import defaultdict
import pymorphy2

nltk.download('punkt')
nltk.download('stopwords')

morph = pymorphy2.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))
tokenizer = RegexpTokenizer(r'\b[а-яё]{2,}\b', flags=re.IGNORECASE)

def preprocess_text(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def tokenize_and_filter(text):
    tokens = tokenizer.tokenize(text)
    return [t.lower() for t in tokens if t.lower() not in stop_words and not t.isdigit()]

def lemmatize(tokens):
    lemmas = []
    for token in tokens:
        parsed = morph.parse(token)
        lemma = None
        for p in parsed:
            if 'ADVB' in p.tag:  # Приоритет для наречий (например, "ясно")
                lemma = p.normal_form
                break
        if not lemma:
            lemma = parsed[0].normal_form
        lemmas.append(lemma.lower())
    return lemmas

def build_inverted_index(folder_path):
    index = defaultdict(set)
    doc_mapping = []

    file_names = sorted(
        [f for f in os.listdir(folder_path) if f.endswith('.txt')],
        key=lambda x: int(x.split('.')[0])
    )

    for doc_id, file_name in enumerate(file_names):
        with open(os.path.join(folder_path, file_name), 'r', encoding='utf-8') as f:
            text = f.read()

        processed = preprocess_text(text)
        tokens = tokenize_and_filter(processed)
        lemmas = lemmatize(tokens)

        for lemma in lemmas:
            index[lemma].add(doc_id)

        doc_mapping.append(file_name)

    return index, doc_mapping

def save_index(index, doc_mapping, output_file='inverted_index.txt'):
    with open(output_file, 'w', encoding='utf-8') as f:
        for lemma in sorted(index.keys()):
            doc_ids = sorted(index[lemma])
            files = [doc_mapping[i] for i in doc_ids]
            f.write(f"{lemma}: {doc_ids} -> {files}\n")

if __name__ == "__main__":
    folder_path = '../Work1/result/article_list/'  # Путь к документам
    index, doc_mapping = build_inverted_index(folder_path)
    save_index(index, doc_mapping)
    print(f"Индекс создан. Документов: {len(doc_mapping)}")