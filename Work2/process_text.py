import os
from nltk.corpus import stopwords
import nltk
from common import lemmatize_tokens, tokenize, clean_html

nltk.download('stopwords')
russian_stopwords = set(stopwords.words('russian'))

def process_files(folder_path):
    seen_tokens = set()
    all_tokens = []
    for filename in sorted(os.listdir(folder_path), key=lambda x: int(x.split('.')[0])):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                text = clean_html(f.read())
                tokens = tokenize(text)
                for token in tokens:
                    token = token.lower()
                    if token not in seen_tokens and token not in russian_stopwords:
                        seen_tokens.add(token)
                        all_tokens.append(token)
    return all_tokens

def main():
    folder_path = "../Work1/result/article_list"
    tokens = process_files(folder_path)
    lemmas = lemmatize_tokens(tokens)

    with open("tokens.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(tokens))

    with open("lemmas.txt", "w", encoding="utf-8") as f:
        for lemma, words in lemmas.items():
            f.write(f"{lemma} {' '.join(words)}\n")

if __name__ == '__main__':
    main()