import os

lemmas_by_file_list_folder = "../Work2/result"
output_file = os.path.join(os.path.join(os.path.dirname(__file__), "result"), "inverted_index.txt") # Выходной файл

# Генерация инвертированного индекса
def build_inverted_index():
    index = dict()

    for file_name in os.listdir(lemmas_by_file_list_folder):
        if not file_name.endswith("-lemmas.txt"):
            continue

        original_file_name = file_name.replace('-lemmas','')
        with open(os.path.join(lemmas_by_file_list_folder, file_name), 'r', encoding='utf-8') as f:
            for line in f.readlines():
                lemma = line.split(' ')[0]
                if lemma in index:
                    index[lemma].append(original_file_name)
                else:
                    index[lemma] = [original_file_name]
    return index

inverted_index = build_inverted_index()

with open(output_file, 'w', encoding='utf-8') as f:
    for lemma in inverted_index:
        f.write(f'{lemma}: {', '.join(inverted_index[lemma])}\n')
