from flask import Flask, render_template, request, jsonify, send_from_directory
from Work5.vector_search import load_tfidf, load_inverted_index, load_links, vector_search

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


tfidf = load_tfidf("../Work4/result/terms")
index = load_inverted_index("../Work3/result/inverted_index.txt")
links = load_links("../Work1/result/index.txt")

autocomplete_cache = set()
for lemma in index.keys():
    autocomplete_cache.add(lemma)

print(f"✅ Загружено документов: {len(tfidf)}")

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search_api():
    try:
        query = request.json.get("query", "").strip()
        if len(query) < 2:
            return jsonify({"error": "Слишком короткий запрос"})

        results = vector_search(query, tfidf, index, links)
        return jsonify({
            "results": results,
            "stats": {
                "found": len(results)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    term = request.args.get("term", "").lower()
    suggestions = [word for word in autocomplete_cache if term in word][:10]
    return jsonify(suggestions)

# @app.route('/preview/<doc_id>')
# def get_preview(doc_id):
#     try:
#         return send_from_directory(
#             '../Work1/result/article_list',
#             f'{doc_id}.txt',
#             mimetype='text/html'
#         )
#     except FileNotFoundError:
#         return "Документ не найден", 404

if __name__ == "__main__":
    app.run(debug=False)