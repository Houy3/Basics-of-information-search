import os
import json

lemmas_by_file_list_folder = "../Work2/result"
output_file = os.path.join(os.path.join(os.path.dirname(__file__), "result"), "inverted_index.txt") # Выходной файл

# Генерация инвертированного индекса
def build_inverted_index():
    index = dict()

    for file_name in os.listdir(lemmas_by_file_list_folder):
        if not file_name.endswith("-lemmas.txt"):
            continue

        file_id = int(file_name.replace('-lemmas.txt',''))
        with open(os.path.join(lemmas_by_file_list_folder, file_name), 'r', encoding='utf-8') as f:
            for line in f.readlines():
                lemma = line.split(' ')[0]
                if lemma in index:
                    index[lemma].append(file_id)
                else:
                    index[lemma] = [file_id]
    return index

inverted_index = build_inverted_index()

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(json.dumps(inverted_index, indent=1, ensure_ascii=False))
