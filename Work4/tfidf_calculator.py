import os
import math
from collections import defaultdict
from tqdm import tqdm

def load_lemmas(lemmas_file):
    lemmas_dict = {}
    try:
        with open(lemmas_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                lemma = parts[0]
                tokens = parts[1:] if len(parts) > 1 else []
                lemmas_dict[lemma] = tokens
    except Exception as e:
        tqdm.write(f"⚠️ Ошибка загрузки {lemmas_file}: {str(e)}")
    return lemmas_dict

def calculate_tf(tokens):
    tf = defaultdict(float)
    total = len(tokens)
    if total == 0:
        return tf
    for token in tokens:
        tf[token] += 1
    return {k: v / total for k, v in tf.items()}

def calculate_idf(docs_items):
    idf = defaultdict(float)
    total_docs = len(docs_items)
    if total_docs == 0:
        return idf

    doc_freq = defaultdict(int)
    for doc in tqdm(docs_items, desc="📊 IDF", unit="док"):
        unique_items = set(doc)
        for item in unique_items:
            doc_freq[item] += 1

    return {
        item: max(0.0, math.log((total_docs + 1) / (count + 1)) + 1)
        for item, count in doc_freq.items()
    }

def process_tfidf():
    input_dir = "../Work2/result"
    output_dir = "result"
    os.makedirs(f"{output_dir}/terms", exist_ok=True)
    os.makedirs(f"{output_dir}/lemmas", exist_ok=True)

    files = [
        f.split("-lemmas.txt")[0]
        for f in os.listdir(input_dir)
        if f.endswith("-lemmas.txt")
    ]

    all_data = []
    for name in tqdm(files, desc="📂 Загрузка"):
        lemma_file = os.path.join(input_dir, f"{name}-lemmas.txt")
        token_file = os.path.join(input_dir, f"{name}-tokens.txt")

        if not os.path.exists(lemma_file):
            tqdm.write(f"🚨 Файл {lemma_file} не найден")
            continue
        if not os.path.exists(token_file):
            tqdm.write(f"🚨 Файл {token_file} не найден")
            continue

        lemmas = load_lemmas(lemma_file)
        try:
            with open(token_file, 'r', encoding='utf-8') as f:
                tokens = [line.strip() for line in f if line.strip()]
        except Exception as e:
            tqdm.write(f"🚨 Ошибка {token_file}: {e}")
            continue

        all_data.append((name, lemmas, tokens))

    idf_terms = calculate_idf([d[2] for d in all_data])
    idf_lemmas = calculate_idf([list(d[1].keys()) for d in all_data])

    for name, lemmas, tokens in tqdm(all_data, desc="🔧 Обработка"):
        tf_terms = calculate_tf(tokens)

        try:
            with open(f"{output_dir}/terms/{name}_terms.txt", "w", encoding="utf-8") as f:
                for term, tf in tf_terms.items():
                    idf_val = idf_terms.get(term, 0.0)
                    tfidf_val = tf * idf_val
                    f.write(f"{term} {idf_val:.4f} {tfidf_val:.4f}\n")
        except Exception as e:
            tqdm.write(f"🚨 Ошибка записи terms {name}: {e}")

        total_terms = len(tokens)
        if total_terms == 0:
            continue

        lemma_scores = {}
        for lemma, words in lemmas.items():
            count = sum(1 for token in tokens if token in words)
            tf_lemma = count / total_terms
            lemma_scores[lemma] = tf_lemma * idf_lemmas.get(lemma, 0.0)

        try:
            with open(f"{output_dir}/lemmas/{name}_lemmas.txt", "w", encoding="utf-8") as f:
                for lemma, score in lemma_scores.items():
                    idf_val = idf_lemmas.get(lemma, 0.0)
                    f.write(f"{lemma} {idf_val:.4f} {score:.4f}\n")
        except Exception as e:
            tqdm.write(f"🚨 Ошибка записи lemmas {name}: {e}")

if __name__ == "__main__":
    process_tfidf()