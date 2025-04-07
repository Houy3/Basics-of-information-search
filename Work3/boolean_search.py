import os
import re
from collections import defaultdict

class BooleanSearchEngine:
    def __init__(self, index_path, doc_folder):
        self.inverted_index, self.doc_mapping = self._load_index(index_path, doc_folder)
        self.all_docs = set(range(len(self.doc_mapping)))

    def _load_index(self, index_path, doc_folder):
        # Сортируем файлы по числовому значению в имени
        doc_mapping = sorted(
            [f for f in os.listdir(doc_folder) if f.endswith('.txt')],
            key=lambda x: int(x.split('.')[0])
        )

        # Создаем обратное отображение: имя файла -> его индекс в doc_mapping
        filename_to_id = {name: idx for idx, name in enumerate(doc_mapping)}

        # Парсим обратный индекс
        index = defaultdict(set)
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' not in line: continue
                lemma_part, docs_part = line.strip().split(':', 1)
                lemma = lemma_part.strip().lower()

                # Извлекаем имена файлов и конвертируем в ID
                doc_files = [fn.strip() for fn in docs_part.split(',')]
                doc_ids = [filename_to_id[fn] for fn in doc_files if fn in filename_to_id]

                index[lemma].update(doc_ids)

        return index, doc_mapping

    # Преобразует поисковый запрос в список токенов для обработки.
    def _parse_query(self, query):
        tokens = re.findall(r'\(|\)|(\bAND\b|\bOR\b|\bNOT\b)|([а-яё]+)', query, re.IGNORECASE)
        return [t[0].upper() if t[0] else t[1].lower() for t in tokens if any(t)]

    def _shunting_yard(self, tokens):
        """Преобразует инфиксную нотацию запроса в постфиксную (обратную польскую) с использованием алгоритма сортировочной станции.

            Основные этапы обработки:
            1. Обработка скобок: '(' помещается в стек, ')' выталкивает операторы из стека пока не встретится '('
            2. Управление приоритетами операторов:
               - NOT (высший приоритет 3)
               - AND (приоритет 2)
               - OR (низший приоритет 1)
            3. Построение выходной последовательности в постфиксной нотации

            Пример преобразования:
                Вход: ['(', 'A', 'AND', 'B', ')', 'OR', 'C']
                Выход: ['A', 'B', 'AND', 'C', 'OR']

            Примечания:
                - Гарантирует правильный порядок выполнения логических операций
                - Сохраняет оригинальный порядок термов
                - Обрабатывает вложенные скобки
            """
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
        """Вычисляет результат постфиксного булева запроса с использованием стека.

            Обрабатывает операторы и термины в обратной польской нотации:
            1. Для терминов: добавляет соответствующий набор документов из индекса
            2. Для операторов:
               - NOT: вычисляет дополнение (все документы минус текущий набор)
               - AND: пересечение двух последних наборов (левый & правый)
               - OR: объединение двух последних наборов (левый | правый)

            Пример вычисления:
                Постфикс: ['A', 'B', 'AND', 'C', 'OR']
                Результат: (A ∩ B) ∪ C

            Примечания:
                - Порядок операндов важен: AND/OR обрабатывают два верхних элемента стека
                - Для неизвестных терминов используется пустое множество
                - Пустой стек возвращает пустое множество
                - NOT применяется только к последнему элементу стека
            """
        stack = []
        for token in postfix:
            if token == 'NOT':
                stack.append(self.all_docs - stack.pop())
            elif token == 'AND':
                right = stack.pop()
                left = stack.pop()
                stack.append(left & right)
            elif token == 'OR':
                right = stack.pop()
                left = stack.pop()
                stack.append(left | right)
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
    engine = BooleanSearchEngine('./result/inverted_index.txt', '../Work1/result/article_list/')
    print("\033[1;36m" + "=== Булев поиск ===" + "\033[0m")
    print("\033[90mДоступные операторы: AND, OR, NOT, скобки\033[0m")
    print("\033[90mВведите 'help' для справки или 'exit' для выхода\033[0m")

    while True:
        try:
            query = input("\n\033[1;34mЗапрос:\033[0m ").strip()
            if not query:
                continue

            if query.lower() == 'exit':
                print("\033[1;33m\nЗавершение работы...\033[0m")
                break

            if query.lower() == 'help':
                print("\n\033[1;35mСправка:\033[0m")
                print("  \033[1;37mФормат запросов:\033[0m")
                print("  - Логические операторы: \033[1;33mAND\033[0m, \033[1;33mOR\033[0m, \033[1;33mNOT\033[0m")
                print("  - Группировка: \033[1;33m()\033[0m")
                print("  - Регистр не важен для операторов и терминов\n")
                print("  \033[1;37mПримеры:\033[0m")
                print("  \033[1;32m• (кошка AND собака) NOT птица\033[0m")
                print("  \033[1;32m• яблоко OR апельсин\033[0m")
                print("  \033[1;32m• (вирус OR бактерия) AND человек\033[0m")
                continue

            results = engine.search(query)

            # Форматирование вывода
            print("\n" + "─" * 50)
            print(f"\033[1;35mПоисковый запрос:\033[0m \033[1;37m{query}\033[0m")
            print(f"\033[1;35mНайдено документов:\033[0m \033[1;36m{len(results)}\033[0m")

            if results:
                print("\n\033[1;32mРезультаты:\033[0m")
                for i, doc in enumerate(results, 1):
                    print(f"  \033[1;34m{i:2d}.\033[0m {doc}")
            else:
                print("\n\033[1;31mСовпадений не найдено\033[0m")

            print("─" * 50)

        except KeyboardInterrupt:
            print("\n\033[1;33mРабота завершена\033[0m")
            break

if __name__ == "__main__":
    main()