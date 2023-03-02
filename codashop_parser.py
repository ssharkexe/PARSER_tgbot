# Парсер сайта codashop (через graphql)

import requests, dbdata as db, json

# coda_url_dict = {
#     'PUBG':'/de/pubg-mobile-uc-redeem-code',
#     'Mobile Legends':'/de/mobile-legends',
#     'Free Fire':'/de/free-fire',
#     'Punishing: Grey Raven':'/de/punishing-gray-raven',
#     'World War Heroes':'/de/world-war-heroes',
#     'The Lord of the Rings: Rise to War':'/de/the-lord-of-the-rings-rise-to-war',
#     '8 Ball Pool':'/de/8-ball-pool',
#     'Time Raiders':'/de/time-raiders',
#     'Captain Tsubasa: Dream Team':'/de/captain-tsubasa-dream-team',
#     'Starfall Fantasy: Neverland':'/de/starfall-fantasy-neverland',
#     'Lost Sanctuary: Eternal Origin':'/de/lost-sanctuary-eternal-origin',
#     'Mirage: Perfect Skyline':'/de/mirage-perfect-skyline',
#     'Tamashi: Rise of Yokai':'/de/tamashi-rise-of-yokai',
#     'Sprite Fantasia':'/de/sprite-fantasia',
#     'Dawn Era':'/de/dawn-era',
#     'Thetan Arena':'/de/thetan-arena',
#     'Super Sus':'/de/super-sus',
#     'Cave Shooter':'/de/cave-shooter',
#     'Wesward Adventure':'/de/westward-adventure',
#     'Arena Mania: Magic Heroes':'/de/arena-mania-magic-heroes',
#     'Miko Era: Twelve Myths':'/de/miko-era-twelve-myths',
#     }
    
# seagm_url_dict = {
#     'PUBG':'/fr/pubg-mobile',
#     'Mobile Legends':'/fr/mobile-legends',
#     'Free Fire':'/fr/free-fire-battlegrounds',
#     'Punishing: Grey Raven':'/fr/punishing-gray-raven',
#     'World War Heroes':'/fr/world-war-heroes',
#     'The Lord of the Rings: Rise to War':'/fr/lotr-rise-to-war-gems',
#     '8 Ball Pool':'/fr/8-ball-pool-coin-cash',
#     'Tamashi: Rise of Yokai':'/fr/tamashi-rise-of-yokai',
#     'Captain Tsubasa: Dream Team':'/fr/captain-tsubasa-dream-team',
#     }

# Функция получения JSON ответа c данными от codashop
def get_codashop_data(game_id, shop_id):
    try:
        game_url = db.GameUrl.get(db.GameUrl.game_id == game_id, db.GameUrl.shop_id == shop_id).url # !!! хардкод для выборки url по ключу 1 (codashop) - заменить на универсальный код
        #Параметры для подключения к api codashop 
        access_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsIlgtaWF0IjoxNjc0NDgwODk4NzMzfQ.eyJvcGVyYXRpb25OYW1lIjoiR2V0UHJvZHVjdFBhZ2VJbmZvIiwicXVlcnkiOiJxdWVyeSBHZXRQcm9kdWN0UGFnZUluZm8oICRwcm9kdWN0VXJsOiBTdHJpbmchLCAkc2hvcExhbmc6IFN0cmluZykge1xuICAgIGdldFByb2R1Y3RQYWdlSW5mbyhwcm9kdWN0VXJsOiAkcHJvZHVjdFVybCwgc2hvcExhbmc6ICRzaG9wTGFuZykge1xuICAgICAgICBnYW1lVXNlcklucHV0IHtcbiAgICAgICAgICAgIHNlY3Rpb25UaXRsZSxcbiAgICAgICAgICAgIGltYWdlSGVscGVyVXJsLFxuICAgICAgICAgICAgaW5zdHJ1Y3Rpb25UZXh0LFxuICAgICAgICAgICAgZmllbGRzIHtcbiAgICAgICAgICAgICAgICBkYXRhIHtcbiAgICAgICAgICAgICAgICAgICAgdGV4dCwgdmFsdWUsIHBhcmVudFZhbHVlXG4gICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgICAgICBwbGFjZUhvbGRlcixcbiAgICAgICAgICAgICAgICBwdWJsaXNoZXIsXG4gICAgICAgICAgICAgICAgbG9nb3V0VXJsLFxuICAgICAgICAgICAgICAgIHR5cGUsIG5hbWUsIGRpc3BsYXlNb2RlLCBkaXNwbGF5T25seSwgcGFyZW50RmllbGQsIHJlZ2V4TmFtZSwgaGFzUGFyZW50aGVzaXMsIGhhc0NvdW50cnlDb2RlLCBsZW5ndGgsIHZhbHVlLCBzY29wZSwgb2F1dGhVcmwsIHJlc3BvbnNlVHlwZSwgY2xpZW50SWRcbiAgICAgICAgICAgIH0sXG4gICAgICAgICAgICB2b3VjaGVyU2VjdGlvblRpdGxlLCB2b3VjaGVyQ2F0ZWdvcnlTZWN0aW9uVGl0bGUsIHZvdWNoZXJJdGVtU2VjdGlvblRpdGxlXG4gICAgICAgICAgICBwYXltZW50U2VjdGlvblRpdGxlLFxuICAgICAgICAgICAgYnV5U2VjdGlvblRpdGxlXG4gICAgICAgIH0sXG4gICAgICAgIHByb2R1Y3RJbmZvIHtcbiAgICAgICAgICAgIGlkLCBndnRJZCwgbmFtZSwgc2hvcnROYW1lLCBwcm9kdWN0VGFnbGluZSwgc2hvcnREZXNjcmlwdGlvbiwgbG9uZ0Rlc2NyaXB0aW9uLCBtZXRhRGVzY3JpcHRpb24sIGxvZ29Mb2NhdGlvbiwgcHJvZHVjdFVybCwgdm91Y2hlclR5cGVOYW1lLCB2b3VjaGVyVHlwZUlkLCBvcmRlclVybCwgcHJvZHVjdFRpdGxlLCB2YXJpYWJsZURlbm9tUHJpY2VNaW5BbW91bnQsIHZhcmlhYmxlRGVub21QcmljZU1heEFtb3VudFxuICAgICAgICB9LFxuICAgICAgICBkZW5vbWluYXRpb25Hcm91cHMge1xuICAgICAgICAgICAgZGlzcGxheVRleHQsXG4gICAgICAgICAgICBkaXNwbGF5SWQsXG4gICAgICAgICAgICBwcmljZVBvaW50cyB7XG4gICAgICAgICAgICAgICAgaWQsXG4gICAgICAgICAgICAgICAgYmVzdGRlYWwsXG4gICAgICAgICAgICAgICAgcGF5bWVudENoYW5uZWwge1xuICAgICAgICAgICAgICAgICAgICBpZCwgZGlzcGxheU5hbWUsIGltYWdlVXJsLCBzdGF0dXMsIHRhZ2xpbmUsIHNvcnRPcmRlciwgdHV0b3JpYWxUeXBlLCB0dXRvcmlhbFVSTCwgc3RhdHVzTWVzc2FnZSwgdHV0b3JpYWxMYWJlbCwgaXNQcm9tb3Rpb24sIHByb21vdGlvblRleHQsIGlzTW5vLFxuICAgICAgICAgICAgICAgICAgICBpbmZvTWVzc2FnZXMge1xuICAgICAgICAgICAgICAgICAgICAgICAgaWNvbixcbiAgICAgICAgICAgICAgICAgICAgICAgIHRleHRcbiAgICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgcHJpY2UgeyBjdXJyZW5jeSwgYW1vdW50fSxcbiAgICAgICAgICAgICAgICBpc1ZhcmlhYmxlUHJpY2UsXG4gICAgICAgICAgICAgICAgaGFzRGlzY291bnQsXG4gICAgICAgICAgICAgICAgcHVibGlzaGVyUHJpY2UsXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgc3RyaWtldGhyb3VnaFByaWNlLFxuICAgICAgICAgICAgc29ydE9yZGVySWQsXG4gICAgICAgICAgICBoYXNTdG9jayxcbiAgICAgICAgICAgIHN0YXR1cyxcbiAgICAgICAgICAgIGlzVmFyaWFibGVEZW5vbSxcbiAgICAgICAgICAgIGRlbm9tSW1hZ2VVcmwsXG4gICAgICAgICAgICBkZW5vbUNhdGVnb3J5SWQsXG4gICAgICAgICAgICBkZW5vbURldGFpbHNUaXRsZSxcbiAgICAgICAgICAgIGRlbm9tRGV0YWlsc0ltYWdlVXJsLFxuICAgICAgICAgICAgb3JpZ2luYWxTa3UsXG4gICAgICAgICAgICB2b3VjaGVySWQsXG4gICAgICAgICAgICBmbGFzaFNhbGVQcm9tb0RldGFpbCB7XG4gICAgICAgICAgICAgICAgcHJvbW9Vc2FnZVxuICAgICAgICAgICAgICAgIHByb21vRW5kRGF0ZVxuICAgICAgICAgICAgfVxuICAgICAgICB9LFxuICAgICAgICBwYXltZW50Q2hhbm5lbHN7IGlkLCBkaXNwbGF5TmFtZSwgaW1hZ2VVcmwsIHN0YXR1cywgc29ydE9yZGVyLCBpc1Byb21vdGlvbiwgcHJvbW90aW9uVGV4dCwgaXNNbm9cbiAgICAgICAgICAgICAgICAgICAgICAgIGJ1eUlucHV0cyB7XG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICBsYWJlbCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIGJ1eUlucHV0RmllbGRzIHtcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICB0eXBlLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHJlcXVpcmVkLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHBsYWNlSG9sZGVyLFxuICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIG1pbkxlbmd0aCxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBtYXhMZW5ndGgsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgbmFtZSxcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICByZWdleE5hbWUsXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgaGFzQ291bnRyeUNvZGVcbiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICAgICAgICAgIH0sXG4gICAgICAgICAgICAgICAgICAgICAgICBpbmZvTWVzc2FnZXMge1xuICAgICAgICAgICAgICAgICAgICAgICAgICAgIGljb24sXG4gICAgICAgICAgICAgICAgICAgICAgICAgICAgdGV4dFxuICAgICAgICAgICAgICAgICAgICAgICAgfSxcbiAgICAgICAgICAgIHN1cmNoYXJnZU5vdGUsIHN1cmNoYXJnZUxpbmssIGlzUmlza0NoZWNraW5nRW5hYmxlZFxuICAgICAgICB9LFxuICAgICAgICBmYXFzIHtcbiAgICAgICAgICAgIHF1ZXN0aW9uLFxuICAgICAgICAgICAgYW5zd2VyXG4gICAgICAgIH0sXG4gICAgICAgIGNvbmZpcm1hdGlvbkRpYWxvZ1NjaGVtYSB7XG4gICAgICAgICAgY29uZmlybWF0aW9uRmllbGRzIHtcbiAgICAgICAgICAgIGxhYmVsLFxuICAgICAgICAgICAgdmFsdWUge1xuICAgICAgICAgICAgICB0eXBlLFxuICAgICAgICAgICAgICBmaWVsZFxuICAgICAgICAgICAgfVxuICAgICAgICAgIH0sXG4gICAgICAgICAgaW52YWxpZFVzZXJFcnJvclNjaGVtYSB7XG4gICAgICAgICAgICBlcnJvckhlYWRlciwgZXJyb3JNZXNzYWdlLCBmaWVsZE5hbWVcbiAgICAgICAgICB9XG4gICAgICAgIH0sXG4gICAgICAgIGhyZWZMaW5rcyB7XG4gICAgICAgICAgICBocmVmTGFuZyxcbiAgICAgICAgICAgIGhyZWZcbiAgICAgICAgfSxcbiAgICAgICAgY2FzaGJhY2tDYW1wYWlnbiB7XG4gICAgICAgICAgICBjYW1wYWlnbklkLFxuICAgICAgICAgICAgcGVyY2VudGFnZSxcbiAgICAgICAgICAgIHBheW1lbnRDaGFubmVsSWRzLFxuICAgICAgICAgICAgc2t1cyxcbiAgICAgICAgICAgIGRlc2NyaXB0aW9uLFxuICAgICAgICAgICAgY2FzaGJhY2tEZW5vbVByaWNlIHtcbiAgICAgICAgICAgICAgcGF5bWVudENoYW5uZWxJZCxcbiAgICAgICAgICAgICAgdm91Y2hlcklkLFxuICAgICAgICAgICAgICBjYXNoYmFja1ByaWNlXG4gICAgICAgICAgICB9LFxuICAgICAgICAgICAgcXVhbGlmeWluZ1VzZXJzXG4gICAgICAgIH0sXG4gICAgICAgIGRpc3BsYXlJbWFnZSxcbiAgICAgICAgZGVub21pbmF0aW9uQ2F0ZWdvcmllcyB7XG4gICAgICAgICAgICBpZCwgcGFyZW50SWQsIHNvcnRPcmRlciwgbGV2ZWwsIG5hbWUsIHRpdGxlLCBzdWJUaXRsZSwgZGVzY3JpcHRpb24sIGltYWdlVXJsXG4gICAgICAgIH0sXG4gICAgICAgIGlzU2hvd1Byb3ZpbmNlLFxuICAgICAgICBjYXB0dXJlZFB1cmNoYXNlIHtcbiAgICAgICAgICAgIHB1cmNoYXNlRGF0ZSxcbiAgICAgICAgICAgIGRlbm9tSWQsXG4gICAgICAgICAgICBwYXltZW50Q2hhbm5lbElkLFxuICAgICAgICAgICAgZW1haWwsXG4gICAgICAgICAgICBtb2JpbGUsXG4gICAgICAgICAgICBib2xldG9GaXJzdE5hbWUsXG4gICAgICAgICAgICBib2xldG9MYXN0TmFtZSxcbiAgICAgICAgICAgIGJvbGV0b0RPQixcbiAgICAgICAgICAgIGJvbGV0b0NQRk51bWJlcixcbiAgICAgICAgICAgIHVzZXJJZCxcbiAgICAgICAgICAgIHpvbmVJZCxcbiAgICAgICAgICAgIGRlbm9tQ2F0ZWdvcnlJZFxuICAgICAgICB9LFxuICAgICAgICByZXZpZXdTdW1tYXJ5IHtcbiAgICAgICAgICAgIGlzRGlzYWJsZWRJbkNNUyxcbiAgICAgICAgICAgIHN0YXJMYWJlbCxcbiAgICAgICAgICAgIHN0YXJSYXRpbmdVcmwsXG4gICAgICAgICAgICB0cnVzdFNjb3JlLFxuICAgICAgICAgICAgdG90YWxSZXZpZXdzXG4gICAgICAgIH1cbiAgICAgICAgZW5hYmxlUHJvbW9Db2RlXG4gICAgICAgIGVuYWJsZUdpZnRpbmdcbiAgICB9XG59XG4iLCJ2YXJpYWJsZXMiOnsicHJvZHVjdFVybCI6Ii9kZS9wdWJnLW1vYmlsZS11Yy1yZWRlZW0tY29kZSIsInNob3BMYW5nIjoiIn19.nJT5YyjRYeGEqX2bK6hTO8-hEij1ZwR2VKWz5lnE4d8'
        query_codashop = "query GetProductPageInfo($productUrl: String!, $shopLang: String) {\n  getProductPageInfo(productUrl: $productUrl, shopLang: $shopLang) {\n    denominationGroups {\n      displayText\n      pricePoints {\n        paymentChannel {\n          displayName\n          }\n        price {\n          amount\n          }\n        publisherPrice\n        }\n      strikethroughPrice}\n      }\n  }"
        headers = {
            'Content-Type':'application/json',
            'Accept':'*/*,application/json',
            'Authorization': f'Bearer {access_token}',
            'Accept-Language': 'ru',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'api-eu.codashop.com',
            'X-SESSION-COUNTRY2NAME': 'DE',
            'path': f'{game_url}',
            'X-XSRF-TOKEN': 'null'
            }
        data = {
            "operationName": "GetProductPageInfo",
            "variables": {
                "productUrl": f'{game_url}', 
                "shopLang":""
            },
            "query": query_codashop
        }
        response = requests.post('https://api-eu.codashop.com/spring/api/graphql', headers=headers, json=data)
        # json_filename = str(f'{game}_{current_game_id}') + '.json'
        # print(json_filename)
        # with open(f'json_data/{json_filename}', "w") as f:
        #     f.write(response.text)
        fetched_data = response.text
        fetched_dict = json.loads(response.text)
        # print(json.dumps(fetched_dict, indent=4))
        # print(json.loads(fetched_dict))
        return codashop_parse(game_id=game_id, data=fetched_data, shop_id=shop_id)
    except db.GameUrl.DoesNotExist:
        return f'{db.Game.get(id=game_id).name} нет в Codashop'

# Функция парсинга JSON ответа c данными от codashop и их запись в таблицу
def codashop_parse(game_id, data, shop_id):
    codashop_data = data
    codashop_data = codashop_data.split('"displayText":"')
    codashop_data.pop(0)
    codashop_data = ', '.join(codashop_data)
    codashop_data = ', '.join(codashop_data.split('","pricePoints":[{"paymentChannel":{"displayName":"'))
    codashop_data = ', '.join(codashop_data.split('"},"price":{"amount":"'))
    codashop_data = ', '.join(codashop_data.split('"},"publisherPrice":"'))
    codashop_data = ', '.join(codashop_data.split('"},{"paymentChannel":{"displayName":"'))
    codashop_data = ', '.join(codashop_data.split('"}],"strikethroughPrice":"'))
    codashop_data = codashop_data.split('"},{, ')
    codashop_data[-1] = codashop_data[-1].replace('"}]}}}', '')
    for i in codashop_data: # парсим список из цен и методов оплаты, для каждого метода из списка db.PaymentChannel отображаем цену (зная, что цена всегда идет после названия метода оплаты)
        game_addon_list = i.split(', ')
        game_addon_default_price = game_addon_list[-1]
        game_addon_name = game_addon_list[0]
        for b in game_addon_list:
            try:
                print(f'Обрабатываем запись {b}, тип оплаты {db.PaymentChannel.get(db.PaymentChannel.name == str(b)).id}, цена {game_addon_list[game_addon_list.index(b)+1]}')
                db.GameAddon.replace(name = game_addon_name, 
                                        game_id = game_id, 
                                        shop_id = shop_id, 
                                        payment_channel_id = db.PaymentChannel.get(db.PaymentChannel.name == str(b)).id,
                                        price = game_addon_list[game_addon_list.index(b)+1],  
                                        currency = 'EUR').execute()
                db.Game(id=game_id).save()
            except db.PaymentChannel.DoesNotExist:
                pass
    return f'Сохранил данные codashop по {db.Game.get(id=game_id).name}'

# def get_game_data(game, shop):
#     current_game_id = game
#     current_shop_id = shop
#     current_game_url = db.GameUrl.get(db.GameUrl.game_id == current_game_id, db.GameUrl.shop_id == current_shop_id).url
#     return current_game_id, current_shop_id, current_game_url


#codashop_parse('pubg_coda')
# get_codashop_data('PUBG', 'Codashop')

# get_codashop_data(6, 1)
