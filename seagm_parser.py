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
    dict1 = dict1.split(',\n    });')[0]
    dict1 = dict1.split('[{')[1]
    dict1 = dict1.split('}]')[0]
    dict1 = dict1.split('},{')
    #print(dict1)
    #dict2 = '{' + dict1[0] + '}'
    #print(dict2)
    #dict2 = json.loads(dict2)
    #print(dict2)
    addons_full_string = f'{game}'
    for i in dict1:
        game_addons = json.loads('{' + i + '}')
        #print(game_addons)
        try:
            discount = game_addons['dbrule_description'].split('Discount: ')[1]
            discount = float(discount.split('%')[0])
        except IndexError as e:
            discount = 0
        full_desc = str(game_addons['item_name']) + ' цена: ' + str(round(float(game_addons['price']) * (1 - discount / 100), 2)) + ' ' + str(game_addons['currency']) + ' (скидка ' + str(discount) + '%)'
        addons_full_string = addons_full_string + '\n' + full_desc
        #print(discount)
        #print(game_addons)
        #print(full_desc)
        #print('--------')
    print(addons_full_string)
    return addons_full_string
    #game1 = dict.fromkeys(dict1)
