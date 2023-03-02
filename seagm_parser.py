# Парсер сайта seagm

import requests, re, json, dbdata as db
from bs4 import BeautifulSoup

# Список URL для парсинга seagm
seagm_url_dict = {
    'pubg_seagm':'https://www.seagm.com/fr/pubg-mobile',
    'legends_seagm':'https://www.seagm.com/fr/mobile-legends',
    'freefire_seagm':'https://www.seagm.com/fr/free-fire-battlegrounds',
    'punishing_seagm':'https://www.seagm.com/fr/punishing-gray-raven',
    'wwh_seagm':'https://www.seagm.com/fr/world-war-heroes',
    'lotr_seagm':'https://www.seagm.com/fr/lotr-rise-to-war-gems',
    'pool_seagm':'https://www.seagm.com/fr/8-ball-pool-coin-cash',
    'tamashi_seagm':'https://www.seagm.com/fr/tamashi-rise-of-yokai',
    'tsubasa_seagm':'https://www.seagm.com/fr/captain-tsubasa-dream-team',
    }

# Параметры для html запросов
html_parameters = {'lang': 'en'}

# Получаем html по игре
def get_seagm_data(game_id, shop_id):
    try:
        addon_url = db.Shop.get(id=shop_id).url
        game_url = ''.join([addon_url, db.GameUrl.get(db.GameUrl.game_id == game_id, db.GameUrl.shop_id == shop_id).url])
        print(game_url)
        response = requests.get(game_url, html_parameters) 
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(soup)
        # with open(f'html_data/{html_filename}', "w") as f:
        #     f.write(response.text)
        return seagm_parse(game_id, soup, shop_id)
    except db.GameUrl.DoesNotExist:
        return f'{db.Game.get(id=game_id).name} нет в SEAGM'

# Функция парсинга страницы seagm с аддонами
def seagm_parse(game_id, data, shop_id):
    # html_filename = str(list(seagm_url_dict.keys())[list(seagm_url_dict.keys()).index(game)]) + '.html'
    # for name, link in seagm_url_dict.items(): # из параметра game (это урл игры из словаря) выбираем название игры
    #     if link == game:
    #         print(f'Цены на аддоны к {name}:')
    #     else:
    #         pass
    # with open(f'html_data/{html_filename}') as fp: 
    #     soup = BeautifulSoup(fp, "html.parser") 
    data = data.find(string=re.compile('gtmDataObject'))
    try:
        data = data.split('prodectBuyList: ')[1]
    except AttributeError:
        print('Некорректный url для игры на seagm.com')
        return f'Некорректный url для игры на seagm.com' # seagm_parse_giftcard(game)
    else:
        return seagm_final_parse(game_id, data, shop_id)

# Функция парсинга страницы seagm с аддонами
def seagm_addon_parse(url, game):
    response = requests.get(url, html_parameters)
    soup = BeautifulSoup(response.content, "html.parser")
    dict1 = soup.find(string=re.compile('gtmDataObject'))
    try:
        dict1 = dict1.split('prodectBuyList: ')[1]
    except AttributeError:
        print('Ошибка парсинга')
    else:
        return f'Некорректный url для игры на seagm.com' # seagm_final_parse(dict1, game)

# Тестовая функция для парсинга html seagm со списком гифткарт для игры
def seagm_parse_giftcard(game):
    html_filename = str(list(seagm_url_dict.keys())[list(seagm_url_dict.keys()).index(game)]) + '.html'
    with open(f'html_data/{html_filename}') as fp: 
        soup = BeautifulSoup(fp, "html.parser") 
    html_data = soup.find_all(attrs={'ga-enecommerce':re.compile(r'gamehome&&[^"]')})
    #print(html_data)
    addons = [match.groups() for match in re.finditer(r'href="([^"]+)" title="([^"]*)"', str(html_data))] # !!! находим все (аддны, пополнения и тд) кроме гифткарт
    giftcard_name_list = [giftcard[1] for giftcard in addons] # сохраняем через цикл перечень названий гифткарт в список
    giftcard_url_list = ['https://www.seagm.com' + giftcard[0] for giftcard in addons] # сохраняем через цикл перечень url
    giftcard_len = len(giftcard_url_list) # сохраняем длину списка гифткарт, чтобы потом обратиться к нужной ссылке по индексу
    print(giftcard_name_list)
    print(giftcard_url_list)
    return giftcard_name_list, giftcard_url_list

def seagm_final_parse(game_id, data, shop_id):
    result = [match.groups() for match in re.finditer(r'"item_name":"([a-zA-Z0-9 ._+-]+)","price":"([0-9.]+)"[^}{]*"discount":"([0-9 .]+)","currency":"([A-Z]+)"', data)]
    # addons_full_string = f'🔹 {game} 🔹\n'
    # print(result)
    for i in result:
        # full_desc = f'{i[0]} - {round(float(i[1])-float(i[2]), 2)} {i[3]}'
        # addons_full_string = addons_full_string + '\n' + full_desc
        try:
            price = round(float(i[1])-float(i[2]), 2)
            print(f'Обрабатываем запись {i[0]}, тип оплаты кредитка (2), цена {price}')
            db.GameAddon.replace(name = i[0], 
                                    game_id = game_id, 
                                    shop_id = shop_id, 
                                    payment_channel_id = 2,
                                    price = price,  
                                    currency = i[3]).execute()
            db.Game(id=game_id).save()
        except db.PaymentChannel.DoesNotExist:
            pass
    return f'Сохранил данные seagm по {db.Game.get(id=game_id).name}'

#seagm_parse_giftcard('rampage')
#get_html_content('rampage')
#seagm_parse_giftcard('pubg_addons_seagm')
# get_seagm_data(1, 2)