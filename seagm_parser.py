# Парсер сайта seagm

import requests, re, dbdata as db
from bs4 import BeautifulSoup
from requests import utils

# Параметры для html запросов
html_parameters = {'accept-language': 'en-US', 
                   'user-Agent': 'Mozilla/5.0'}

headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type':'application/x-www-form-urlencoded',
            'content-length': '121',
            'origin': 'https://www.seagm.com',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "macOS",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }

headers2 = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }

cookies = {
    'seagm_store_id':'lf1sof51i9r28ql3or03kfiflu',
    '__cf_bm':'QZ6qOlY4ixwzznfAmI0APTrqG6qKy5A0uaW6242mYM-1678012716-0-AZEt8oGcp4gSXyj4UdjZq3S02FsI9B3v924x0a9h7eax5gM71N0oPNf2+AGYA5TNVlH4C7AweGs0vzW/m4rqEaJYDWhy9KP4fBShbqqX8ySZeia/HEdcKhsruIaDimQ5pbbDUpZHUiXe67UejvN3jPg='
}

# у SEAGM есть фиксированная комиссия (процент и фикс) при оплате картой, сохраним ее в переменную
fee_percent = float(1.029)
fee_fix = float(0.21)

# Получаем html по игре
def get_seagm_data(game_id: int, shop_id: int, region_code: str) -> str:
    try:
        shop_url = db.Shop.get(id=shop_id).url
        game_url = f'/{region_code}/{db.GameUrl.get(db.GameUrl.game_id == game_id, db.GameUrl.shop_id == shop_id).url}'
        full_url = f'{shop_url}{game_url}'
        p = requests.Session()
        get_request = p.get(full_url)
        csrf_token = re.search(r'csrfToken=([a-zA-Z0-9]+)"', get_request.text).groups()[0] # type: ignore
        print(f'csrf = {csrf_token}')
        CUR = 'EUR'
        post_header = {            
                    'content-type':'application/x-www-form-urlencoded',
                    'origin': 'https://www.seagm.com',
                    'referer': f'{full_url}',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        post_params = {'region': f'{region_code}', 'region_lang': 'none', 'language': 'en', 'currency': f'{CUR}', 'request_uri': f'{game_url}'}
        query_params = {'csrfToken': f'{csrf_token}'}
        post_request = p.post(f'{shop_url}/{region_code}/setting', params=query_params, data=post_params, headers=post_header, cookies=p.cookies)
        print(post_request.url)
        print(post_request.status_code)
        response = p.get(full_url, cookies=p.cookies)
        print(re.search(r'Currency: \W([a-zA-Z0-9]+)\W,\s+},', response.text ).groups()[0]) # type: ignore
        p.close()
        if response.status_code == 404:
            return f'🟠 Некорректный url игры на SEAGM'
        else:
            print(utils.dict_from_cookiejar(p.cookies))
            soup = BeautifulSoup(response.text, 'html.parser')
            return seagm_parse(game_id, soup, shop_id, region_code)
    except db.DoesNotExist:
        db.Game(id=game_id).save()
        return f'🔴 {db.Game.get(id=game_id).name} нет в SEAGM'

# Функция парсинга страницы seagm с аддонами
def seagm_parse(game_id: int, soup: BeautifulSoup, shop_id: int, region_code: str):
    data = soup.find(string=re.compile('gtmDataObject'))
    print(f'Тип данныех после soup.find {type(data)}')
    try:
        parse_result: str = data.split('prodectBuyList: ')[1] 
        print(f'Тип данныех после data.split {type(parse_result)}')
    except AttributeError:
        print('Некорректный url для игры на seagm.com')
        return f'🟠 Некорректный url для игры на seagm.com' # seagm_parse_giftcard(game)
    else:
        return seagm_final_parse(game_id, parse_result, shop_id, region_code)

# Функция парсинга страницы seagm с аддонами
def seagm_addon_parse(url: str, game: int) -> str:
    response = requests.get(url, html_parameters)
    soup = BeautifulSoup(response.content, "html.parser")
    dict1 = soup.find(string=re.compile('gtmDataObject'))
    try:
        dict1 = dict1.split('prodectBuyList: ')[1]
    except AttributeError:
        print('Ошибка парсинга')
        return f'🟠 Ошибка парсинга на seagm.com'
    else:
        return f'🟠 Некорректный url для игры на seagm.com' # seagm_final_parse(dict1, game)

# Тестовая функция для парсинга html seagm со списком гифткарт для игры
# def seagm_parse_giftcard(game):
#     html_filename = str(list(seagm_url_dict.keys())[list(seagm_url_dict.keys()).index(game)]) + '.html'
#     with open(f'html_data/{html_filename}') as fp: 
#         soup = BeautifulSoup(fp, "html.parser") 
#     html_data = soup.find_all(attrs={'ga-enecommerce':re.compile(r'gamehome&&[^"]')})
#     #print(html_data)
#     addons = [match.groups() for match in re.finditer(r'href="([^"]+)" title="([^"]*)"', str(html_data))] # !!! находим все (аддны, пополнения и тд) кроме гифткарт
#     giftcard_name_list = [giftcard[1] for giftcard in addons] # сохраняем через цикл перечень названий гифткарт в список
#     giftcard_url_list = ['https://www.seagm.com' + giftcard[0] for giftcard in addons] # сохраняем через цикл перечень url
#     giftcard_len = len(giftcard_url_list) # сохраняем длину списка гифткарт, чтобы потом обратиться к нужной ссылке по индексу
#     print(giftcard_name_list)
#     print(giftcard_url_list)
#     return giftcard_name_list, giftcard_url_list

def seagm_final_parse(game_id: int, data: str, shop_id: int, region_code: str) -> str:
    result = [match.groups() for match in re.finditer(r'"item_name":"([a-zA-Z0-9 ._+-]+)","price":"([0-9.]+)"[^}{]*"discount":"([0-9 .]+)","currency":"([A-Z]+)"', data)]
    for i in result:
        try:
            price = round((float(i[1])-float(i[2])) * fee_percent + fee_fix, 2)
            print(f'Обрабатываем запись {i[0]}, тип оплаты кредитка (2), цена {price}')
            db.GameAddon.replace(name = i[0], 
                                    game_id = game_id, 
                                    shop_id = shop_id, 
                                    payment_channel_id = 2,
                                    price = price,  
                                    currency = i[3],
                                    region = region_code).execute()
            db.Game(id=game_id).save()
        except db.DoesNotExist:
            pass
    return f'🟢 Сохранил данные SEAGM по {db.Game.get(id=game_id).name}'