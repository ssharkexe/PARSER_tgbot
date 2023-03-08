# Парсер сайта seagm

import requests, re, json, dbdata as db
from bs4 import BeautifulSoup
from selenium import webdriver
import time

# Параметры для html запросов
html_parameters = {'accept-language': 'en-US', 
                   'user-Agent': 'Mozilla/5.0'}

headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
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
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }

cookies = {
    'bm_decision':'undefined',
    'seagm_store_id':'2vvlmdfermampe6jjqai4g7365',
    'CS_FPC':'CSCaM6wVSbqcUnOE6U7Pj2wu8fzPUImJW64',
    'CS_CTIME':'1678187268213',
    'shd_NWC':'8b80e4cc66875bbf9291186694467abd',
    '__cfshdid':'CF64071b048af550.86843556',
    '_gcl_au':'1.1.2098671162.1678187269',
    '_tt_enable_cookie':'1',
    '_ttp':'5SBHsrfgRaxaGX4oi1KCntEyltk',
    '_gid':'GA1.2.932077814.1678187269',
    '_gat_UA-187290322-1':'1',
    '_fbp':'fb.1.1678187269542.1384386785',
    '_ga':'GA1.1.1408264654.1678187269',
    '__cf_bm':'ZyjrTvxGwGMOhfs.yxQkjXxQ7Lz3X3WZ3mMP0PJ7N8M-1678187284-0-AZNUlXPU3diN0L+Rb//DT8Dh0HZ/TlUedc2V7vqJscD+S/DOERj7F+jREuu5q4prD/r+Q5+K+ugYETs+TZ4XJxMgfVyL5swYA3F+JDFSGS+54j05K5WfsP1bopwEHckg9g==',
    '_ga_PPNCESN4Z7':'GS1.1.1678187269.1.1.1678187290.39.0.0'
    }

headers3 = {
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://www.seagm.com',
            'referer': 'https://www.seagm.com/es/pubg-mobile-uc-top-up-global',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': "macOS",
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
            }

# s = requests.Session()
# s.close()
# s.headers.update(headers3)
# s.cookies.clear()
# # s.cookies.set('seagm_store_id', 'lf1sof51i9r28ql3or03kfiflu')
# html = s.get('https://www.seagm.com/es/pubg-mobile-uc-top-up-global', headers=headers3, cookies=cookies)
# # resp = requests.get('https://www.seagm.com/es-es/pubg-mobile-uc-top-up-global')
# print(html.text)
# post_params = {'region': 'ru', 'region_lang': 'none', 'language': 'es', 'currency': 'USD', 'request_uri': '/es/pubg-mobile-uc-top-up-global?ps=Game-Home'}
# query_params = {'csrfToken': '1a6ac4381f1caa8d6202754fbfb89de5'}
# resp = s.post("https://www.seagm.com/es/setting", params=query_params, data=post_params, headers=headers3)
# # print(resp.url)
# # my_cookies = requests.utils.dict_from_cookiejar(s.cookies)
# # print(my_cookies)
# print(resp.status_code)
# print(resp.text)
# # resp = s.get('https://www.seagm.com/es/pubg-mobile-uc-top-up-global')

def test(CUR, full_url, url, region):
    p = requests.Session()
    # p.headers.update(headers3)
    get_request = p.get(full_url)
    # store_id = p.cookies.get_dict()['seagm_store_id']
    # print(f'store id = {store_id}')
    csrf_token = re.search(r'csrfToken=([a-zA-Z0-9]+)"', get_request.text).groups()[0]
    print(f'csrf = {csrf_token}')
    post_header = {            
                'content-type':'application/x-www-form-urlencoded',
                'origin': 'https://www.seagm.com',
                'referer': f'{full_url}',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    post_params = {'region': f'{region}', 'region_lang': 'none', 'language': 'en', 'currency': f'{CUR}', 'request_uri': f'{url}'}
    query_params = {'csrfToken': f'{csrf_token}'}
    post_request = p.post(f'https://www.seagm.com/{region}/setting', params=query_params, data=post_params, headers=post_header, cookies=p.cookies)
    print(post_request.url)
    print(post_request.status_code)
    # store_id = p.cookies.get_dict()['seagm_store_id']
    # print(f'store id = {store_id}')
    get_request2 = p.get(full_url, cookies=p.cookies)
    print(re.search(r'Currency: \W([a-zA-Z0-9]+)\W,\s+},', get_request2.text ).groups()[0])
    p.close()

test('EUR', 'https://www.seagm.com/pubg-mobile-uc-top-up-global', '/pubg-mobile-uc-top-up-global', 'fr')
test('USD', 'https://www.seagm.com/pubg-mobile-uc-top-up-global', '/pubg-mobile-uc-top-up-global', 'fr')


# Получаем html по игре
def get_seagm_data(game_id, shop_id, region_code):
    try:
        shop_url = db.Shop.get(id=shop_id).url
        game_url = f'{shop_url}/{region_code}/{db.GameUrl.get(db.GameUrl.game_id == game_id, db.GameUrl.shop_id == shop_id).url}'
        s = requests.Session()
        s.cookies.set('seagm_store_id', 'p999gj39mn09gq5djits0esr0a')
        # post_params = {'region': 'es', 'region_lang': 'none', 'language': 'es', 'currency': 'EUR', 'request_uri': '/es'}
        # resp = requests.post("https://www.seagm.com/es/setting?csrfToken=9513fd10e7fe17d3b55ede554763d921", data=post_params)
        # print(resp.text)
        response = s.get(game_url) 
        if response.status_code == 404:
            return f'🟠 Некорректный url игры на SEAGM'
        else:
            print(requests.utils.dict_from_cookiejar(s.cookies))
            soup = BeautifulSoup(response.text, 'html.parser')
            # print(soup)
            # with open(f'html/test.html', "w") as f:
            #     f.write(response.text)
            return seagm_parse(game_id, soup, shop_id, region_code)
    except db.GameUrl.DoesNotExist:
        return f'{db.Game.get(id=game_id).name} нет в SEAGM'

# Функция парсинга страницы seagm с аддонами
def seagm_parse(game_id, data, shop_id, region_code):
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
        return f'🟠 Некорректный url для игры на seagm.com' # seagm_parse_giftcard(game)
    else:
        return seagm_final_parse(game_id, data, shop_id, region_code)

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
        return f'🟠 Некорректный url для игры на seagm.com' # seagm_final_parse(dict1, game)

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

def seagm_final_parse(game_id, data, shop_id, region_code):
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
                                    currency = i[3],
                                    region = region_code).execute()
            db.Game(id=game_id).save()
        except db.PaymentChannel.DoesNotExist:
            pass
    return f'🟢 Сохранил данные SEAGM по {db.Game.get(id=game_id).name}'

#seagm_parse_giftcard('rampage')
#get_html_content('rampage')
#seagm_parse_giftcard('pubg_addons_seagm')
# get_seagm_data(1, 2)