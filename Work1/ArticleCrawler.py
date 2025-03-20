import os
import shutil
import requests
from bs4 import BeautifulSoup

# Входные параметры
HOME_URL = 'https://animaljournal.ru/' # Главная страничка сайта
ARTICLE_LIST_BY_PAGE_URL = 'https://animaljournal.ru/page/' # Страничка со списком статей
ARTICLE_TITLE_CLASS = 'post_title' # HTML класс тега, в котором ссылка на статью

OUTPUT_DIRECTORY = os.path.join(os.path.dirname(__file__), "result") # Выходная папка
ARTICLE_LIST_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, 'page_list') # Папка со страницами
INDEX_FILE = os.path.join(OUTPUT_DIRECTORY, 'index.txt') # index.txt файл

# подготавливаем все выходные файлы и папки
def prepare_output_directory():
    if os.path.isdir(ARTICLE_LIST_DIRECTORY):
        shutil.rmtree(ARTICLE_LIST_DIRECTORY)

    os.mkdir(ARTICLE_LIST_DIRECTORY)
    open(INDEX_FILE, 'w').close()

# Формируем список ссылок на статьи
def get_article_link_list():
    link_list = []
    for i in range(1, 26): # проходим с 1 по 25 страницу
        response = requests.get(ARTICLE_LIST_BY_PAGE_URL + str(i))
        for link_tag in BeautifulSoup(response.text, 'html.parser').find_all('a', {'class': ARTICLE_TITLE_CLASS}):
            link_list.append(HOME_URL + link_tag.get('href'))
    return link_list

# Выкачать страницу
def get_text(url):
    parser = BeautifulSoup(requests.get(url).text, 'html.parser')
    for tag in parser.find_all(['style', 'link', 'script']): # Убираем все лишнее
        tag.decompose()
    return str(parser)

# Выкачать статьи в файлы
def download_article_list():
    with open(INDEX_FILE, 'w', encoding='utf-8') as index_file:
        i = 1
        for link in get_article_link_list():
            text = get_text(link)
            if len(text) < 300:
                continue

            article_file_name = str(i) + ".txt"
            with open(os.path.join(ARTICLE_LIST_DIRECTORY, article_file_name), 'w', encoding='utf-8') as page_file:
                page_file.write(text)

            index_file.write(article_file_name + " - " + link + "\n")

            i += 1

def zip_article_list():
    shutil.make_archive(ARTICLE_LIST_DIRECTORY, 'zip', ARTICLE_LIST_DIRECTORY)


prepare_output_directory()
download_article_list()
zip_article_list()