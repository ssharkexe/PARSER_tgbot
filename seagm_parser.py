# Парсер сайта seagm

import requests, re, json
from bs4 import BeautifulSoup

# Список URL для парсинга seagm
seagm_url_dict = {
    'pubg_seagm':'https://www.seagm.com/fr/pubg-mobile-uc-top-up-global',
    'legends_seagm':'https://www.seagm.com/fr/mobile-legends-diamonds-top-up',
    'freefire_seagm':'https://www.seagm.com/fr/free-fire-diamonds-top-up',
    }

# Параметры для html запросов
html_parameters = {'lang': 'en'}

# Функция сохранения html в файл
def get_html_content(url):
    html_filename = str(list(seagm_url_dict.keys())[list(seagm_url_dict.keys()).index(url)]) + '.html'
    response = requests.get(seagm_url_dict[url], html_parameters) 
    #soup = BeautifulSoup(response.content, 'html.parser') 
    #print(soup.title.string)
    with open(f'html_data/{html_filename}', "w") as f:
        f.write(response.text)

# Функция парсинга страницы seagm с аддонами
def seagm_parse(game):
    html_filename = str(list(seagm_url_dict.keys())[list(seagm_url_dict.keys()).index(game)]) + '.html'
    for name, link in seagm_url_dict.items(): # из параметра game (это урл игры из словаря) выбираем название игры
        if link == game:
            print(f'Цены на аддоны к {name}:')
        else:
            pass
    with open(f'html_data/{html_filename}') as fp: 
        soup = BeautifulSoup(fp, "html.parser") 
    dict1 = soup.find(string=re.compile('gtmDataObject'))
    dict1 = dict1.split('prodectBuyList: ')[1]
    result = [match.groups() for match in re.finditer(r'"item_name":"([a-zA-Z0-9 ._+-]+)","price":"([0-9.]+)"[^}{]*"discount":"([0-9 .]+)","currency":"([A-Z]+)"', dict1)]
    addons_full_string = f'{game}'
    for i in result:
        full_desc = f'{i[0]} - {round(float(i[1])-float(i[2]), 2)} {i[3]}'
        addons_full_string = addons_full_string + '\n' + full_desc
    print(addons_full_string)
    return addons_full_string

seagm_parse('freefire_seagm')
