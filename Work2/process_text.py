import os

article_list_folder = "../Work1/result/article_list"
OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "result")

from common import process_files, lemmatize_tokens

for file_name in os.listdir(article_list_folder):

    tokens = process_files(os.path.join(article_list_folder, file_name))
    lemmas = lemmatize_tokens(tokens)

    short_file_name = file_name.split('.')[0]

    with open(os.path.join(OUTPUT_DIRECTORY, short_file_name + "-tokens.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))

    with open(os.path.join(OUTPUT_DIRECTORY, short_file_name + "-lemmas.txt"), "w", encoding="utf-8") as f:
        for lemma, words in lemmas.items():
            f.write(f"{lemma} {' '.join(words)}\n")
