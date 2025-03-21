import os
import re
from ast import literal_eval
from collections import defaultdict

class BooleanSearchEngine:
    def __init__(self, index_path, doc_folder):
        self.inverted_index, self.doc_mapping = self._load_index(index_path, doc_folder)
        self.all_docs = set(range(len(self.doc_mapping)))

    def _load_index(self, index_path, doc_folder):
        # Загрузка и сортировка документов
        doc_mapping = sorted(
            [f for f in os.listdir(doc_folder) if f.endswith('.txt')],
            key=lambda x: int(x.split('.')[0])
        )

        # Парсинг файла индекса
        index = defaultdict(set)
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                lemma, rest = line.split(':', 1)
                doc_ids = literal_eval(rest.split('->')[0].strip())
                index[lemma.strip()] = set(doc_ids)

        return index, doc_mapping

    def _parse_query(self, query):
        # Разбиваем запрос на токены
        tokens = re.findall(r'\(|\)|(\bAND\b|\bOR\b|\bNOT\b)|([а-яё]+)', query, re.IGNORECASE)
        return [t[0].upper() if t[0] else t[1].lower() for t in tokens if any(t)]

    def _shunting_yard(self, tokens):
        # Конвертация в обратную польскую нотацию
        stack, output = [], []
        precedence = {'NOT':3, 'AND':2, 'OR':1}

        for token in tokens:
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack[-1] != '(': output.append(stack.pop())
                stack.pop()
            elif token in precedence:
                while stack and stack[-1] != '(' and precedence[token] <= precedence.get(stack[-1],0):
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)

        return output + stack[::-1]

    def _evaluate_postfix(self, postfix):
        # Вычисление постфиксного выражения
        stack = []
        for token in postfix:
            if token == 'NOT':
                stack.append(self.all_docs - stack.pop())
            elif token == 'AND':
                stack.append(stack.pop() & stack.pop())
            elif token == 'OR':
                stack.append(stack.pop() | stack.pop())
            else:
                stack.append(self.inverted_index.get(token, set()))
        return stack.pop() if stack else set()

    def search(self, query):
        try:
            postfix = self._shunting_yard(self._parse_query(query))
            result_ids = self._evaluate_postfix(postfix)
            return [self.doc_mapping[i] for i in sorted(result_ids)]
        except Exception as e:
            print(f"Ошибка: {e}")
            return []

def main():
    engine = BooleanSearchEngine('inverted_index.txt', '../Work1/result/article_list/')
    print("=== Булев поиск ===")
    print("Доступные операторы: AND, OR, NOT, скобки")
    print("Введите 'help' для справки или 'exit' для выхода")

    while True:
        try:
            query = input("\nЗапрос: ").strip()
            if not query: continue

            if query.lower() == 'exit': break
            if query.lower() == 'help':
                print("\nПримеры запросов:")
                print("(кошка AND собака) NOT птица")
                print("яблоко OR апельсин")
                continue

            results = engine.search(query)
            print(f"\nРезультаты ({len(results)}):")
            for doc in results: print(f"- {doc}")

        except KeyboardInterrupt:
            print("\nРабота завершена")
            break

if __name__ == "__main__":
    main()