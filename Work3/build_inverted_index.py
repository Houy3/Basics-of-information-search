import os
import re
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
import pymorphy2
from tqdm import tqdm

from common import read_file_text, contains, clean_html

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

morph = pymorphy2.MorphAnalyzer()
stop_words = set(stopwords.words('russian'))

lemmas_path = "../Work2/lemmas.txt"
tokens_path = "../Work2/tokens.txt"
output_file = 'inverted_index.txt'

def extract_file_number(filename: str) -> int:
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0

def build_inverted_index(path) -> tuple[defaultdict, dict]:
    index = defaultdict(set)
    doc_mapping = {}

    lemmas = read_file_text(lemmas_path).split("\n")

    file_names = sorted(
        [f for f in os.listdir(path) if f.endswith('.txt')],
        key=lambda x: int(''.join(filter(str.isdigit, x.split('.')[0])))
    )

    for doc_id, file_name in tqdm(enumerate(file_names), total=len(file_names), desc="Индексация"):
        file_path = os.path.join(path, file_name)

        file_text = clean_html(read_file_text(file_path)).lower()
        file_tokens = set(file_text.split())

        for lemma_info in lemmas:
            words = lemma_info.split(" ")
            if not lemma_info:
                continue
            lemma = words[0]
            tokens = words[1:]

            for token in tokens:
                if token in file_tokens:
                    index[lemma].add(doc_id)
                    break

        doc_mapping[doc_id] = file_name

    return index, doc_mapping

def save_index(index: defaultdict, doc_mapping: dict) -> None:
    with open(output_file, 'w', encoding='utf-8') as f:
        for lemma in sorted(index.keys()):
            doc_ids = sorted(index[lemma])
            files = [doc_mapping[doc_id] for doc_id in doc_ids]
            files_str = ', '.join(files)
            f.write(f"{lemma}: {files_str}\n")

if __name__ == "__main__":
    folder_path = '../Work1/result/article_list/'
    try:
        index, doc_mapping = build_inverted_index(folder_path)
        save_index(index, doc_mapping)
        print(f"\nИндекс успешно создан. Обработано документов: {len(doc_mapping)}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")