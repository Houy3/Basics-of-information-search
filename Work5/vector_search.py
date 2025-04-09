import os
import math
from collections import defaultdict
from tqdm import tqdm
from pymorphy3 import MorphAnalyzer

def load_tfidf(terms_dir):
    morph = MorphAnalyzer()
    tfidf = defaultdict(dict)
    files = [f for f in os.listdir(terms_dir) if f.endswith("_terms.txt")]

    for file in tqdm(files, desc="[INFO] Загрузка TF-IDF", leave=False):
        doc_id = file.replace("_terms.txt", "")
        try:
            with open(os.path.join(terms_dir, file), "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) != 3:
                        continue
                    term, _, tfidf_val = parts
                    lemma = morph.parse(term)[0].normal_form
                    tfidf[doc_id][lemma] = float(tfidf_val)
        except Exception as e:
            print(f"[ERROR] Ошибка в {file}: {str(e)}")
    return tfidf

def load_inverted_index(index_file):
    index = defaultdict(list)
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            for line in f:
                if ": " not in line:
                    continue
                lemma, docs = line.strip().split(": ", 1)
                index[lemma] = [d.replace(".txt", "") for d in docs.split(", ")]
    except Exception as e:
        print(f"[ERROR] Файл {index_file}: {str(e)}")
    return index

def lemmatize_query(query):
    morph = MorphAnalyzer()
    lemmas = []
    for word in query.split():
        parsed = morph.parse(word.lower())
        if not parsed:
            continue
        lemma = parsed[0].normal_form
        lemmas.append(lemma)
    return lemmas

def vector_search(query, tfidf, index, top_n=10):
    query_terms = lemmatize_query(query)
    if not query_terms:
        return []

    total_docs = len(tfidf)
    idf = {}
    for term in query_terms:
        doc_freq = len(index.get(term, []))
        idf[term] = math.log((total_docs + 1) / (doc_freq + 1e-6)) + 1

    query_tf = {term: query_terms.count(term) / len(query_terms) for term in query_terms}
    query_vec = {term: tf * idf.get(term, 0) for term, tf in query_tf.items()}

    candidates = set()
    for term in query_terms:
        candidates.update(index.get(term, []))

    results = []
    for doc in candidates:
        if doc not in tfidf:
            continue

        doc_vec = tfidf[doc]
        dot = sum(query_vec.get(term, 0) * doc_vec.get(term, 0) for term in query_terms)
        norm_query = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        norm_doc = math.sqrt(sum(v ** 2 for v in doc_vec.values()))

        score = dot / (norm_query * norm_doc) if (norm_query * norm_doc) != 0 else 0.0
        results.append((doc, score))

    return sorted(results, key=lambda x: -x[1])[:top_n]

def main():
    terms_dir = "../Work4/result/terms"
    index_file = "../Work3/result/inverted_index.txt"

    if not os.path.exists(terms_dir):
        print(f"[ERROR] Директория {terms_dir} не существует!")
        return
    if not os.path.exists(index_file):
        print(f"[ERROR] Файл {index_file} не найден!")
        return

    print("🔍 Загрузка данных...")
    tfidf = load_tfidf(terms_dir)
    index = load_inverted_index(index_file)
    print(f"✅ Загружено документов: {len(tfidf)}")

    while True:
        try:
            query = input("\n📝 Введите запрос (exit для выхода): ").strip()
            if query.lower() == 'exit':
                print("\n🛑 Работа завершена")
                break

            results = vector_search(query, tfidf, index)

            if not results:
                print("\n❌ Совпадений не найдено")
                continue

            print("\n🔎 Топ результатов:")
            for i, (doc, score) in enumerate(results[:10], 1):
                print(f"{i:>2}. Док. {doc:<5} | Сходство: {score:.4f}")

        except KeyboardInterrupt:
            print("\n🛑 Поиск отменен")
            break
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")

if __name__ == "__main__":
    main()