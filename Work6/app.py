from flask import Flask, render_template, request, jsonify, send_from_directory
import math
import os
import concurrent.futures
from collections import defaultdict
from pymorphy3 import MorphAnalyzer
from time import perf_counter

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

autocomplete_cache = set()

def load_data():
    morph = MorphAnalyzer()
    tfidf = defaultdict(dict)
    index = defaultdict(list)
    global autocomplete_cache

    def process_tfidf_file(file):
        doc_id = file.replace("_terms.txt", "")
        with open(os.path.join(terms_dir, file), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                term, _, tfidf_val = parts
                lemma = morph.parse(term)[0].normal_form
                tfidf[doc_id][lemma] = float(tfidf_val)
                autocomplete_cache.add(lemma)

    terms_dir = "../Work4/result/terms"
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            files = [f for f in os.listdir(terms_dir) if f.endswith("_terms.txt")]
            executor.map(process_tfidf_file, files)
    except Exception as e:
        print(f"Ошибка загрузки TF-IDF: {str(e)}")

    index_file = "../Work3/result/inverted_index.txt"
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            for line in f:
                if ": " not in line: continue
                lemma, docs = line.strip().split(": ", 1)
                index[lemma] = [d.replace(".txt", "") for d in docs.split(", ")]
    except Exception as e:
        print(f"Ошибка загрузки индекса: {str(e)}")

    return tfidf, index


start_time = perf_counter()
tfidf, index = load_data()
print(f"✅ Данные загружены за {perf_counter() - start_time:.2f} сек")

def vector_search(query):
    morph = MorphAnalyzer()
    query_terms = [
        morph.parse(word.lower())[0].normal_form
        for word in query.split()
        if morph.parse(word.lower())
    ]

    if not query_terms:
        return []

    total_docs = len(tfidf)
    idf = {
        term: math.log((total_docs + 1) / (len(index.get(term, [])) + 1e-6)) + 1
        for term in query_terms
    }

    query_tf = {
        term: query_terms.count(term) / len(query_terms)
        for term in query_terms
    }

    query_vec = {term: tf * idf.get(term, 0) for term, tf in query_tf.items()}
    candidates = set().union(*[index.get(term, []) for term in query_terms])

    results = []
    for doc in candidates:
        doc_vec = tfidf.get(doc, {})
        dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0) for t in query_terms)
        norm_q = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        norm_d = math.sqrt(sum(v ** 2 for v in doc_vec.values()))

        score = dot / (norm_q * norm_d) if (norm_q * norm_d) != 0 else 0
        results.append((doc, score))

    return sorted(results, key=lambda x: -x[1])[:10]

def calculate_score(doc, query_terms, query_vec):
    doc_vec = tfidf.get(doc, {})
    dot = sum(query_vec.get(t, 0) * doc_vec.get(t, 0) for t in query_terms)
    norm_q = math.sqrt(sum(v ** 2 for v in query_vec.values()))
    norm_d = math.sqrt(sum(v ** 2 for v in doc_vec.values()))

    score = dot / (norm_q * norm_d) if (norm_q * norm_d) != 0 else 0
    return (doc, score)


@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_api():
    try:
        query = request.json.get("query", "").strip()
        if len(query) < 2:
            return jsonify({"error": "Слишком короткий запрос"})

        results = vector_search(query)
        return jsonify({
            "results": results,
            "stats": {
                "found": len(results),
                "time": f"{perf_counter() - start_time:.3f} сек"
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    term = request.args.get("term", "").lower()
    suggestions = [word for word in autocomplete_cache if term in word][:10]
    return jsonify(suggestions)

@app.route('/preview/<doc_id>')
def get_preview(doc_id):
    try:
        return send_from_directory(
            '../Work1/result/article_list',
            f'{doc_id}.txt',
            mimetype='text/html'
        )
    except FileNotFoundError:
        return "Документ не найден", 404

if __name__ == "__main__":
    app.run(debug=True)