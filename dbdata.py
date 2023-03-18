from peewee import *
import datetime
import csv

# Создаем соединение с нашей базой данных
db = SqliteDatabase('db.sqlite')

# Определяем базовую модель о которой будут наследоваться остальные
class BaseModel(Model):
    class Meta:
        database = db

# Определяем модель игр
class Game(BaseModel):
    id = AutoField(primary_key = True)
    name = CharField(unique = True, null=False)
    updated_date = DateTimeField(default = datetime.datetime.now)

class Shop(BaseModel):
    id = AutoField(primary_key = True)
    name = CharField(unique = True, null=False)
    url = CharField(unique = True, null=False)

class PaymentChannel(BaseModel):
    id = AutoField(primary_key = True)
    name = CharField(unique = True, null=False)

class PaymentChannelCode(BaseModel):
    code = IntegerField(primary_key = True)
    paymentchannel_id = ForeignKeyField(PaymentChannel)

class Region(BaseModel):
    code = CharField(primary_key = True)
    country = CharField(null=False)

class GameAddon(BaseModel):
    id = AutoField(primary_key = True)
    name = CharField(null=False)
    game_id = ForeignKeyField(Game, backref='addons')
    shop_id = ForeignKeyField(Shop)
    payment_channel_id = ForeignKeyField(PaymentChannel)
    price = FloatField(null=False)
    currency = CharField(null=False)
    region = ForeignKeyField(Region)
    updated = DateTimeField(default = datetime.datetime.now)

    class Meta:
        indexes = (
            # create a unique on name/game/shop/payment
            (('name', 'game_id', 'shop_id', 'payment_channel_id', 'region'), True),)

class GameUrl(BaseModel):
    id = AutoField(primary_key = True)
    game_id = ForeignKeyField(Game, backref='urls')
    shop_id = ForeignKeyField(Shop)
    url = CharField(null=False)
    added = DateTimeField(default = datetime.datetime.now)

    class Meta:
        indexes = (
            # create a unique on game/shop/url
            (('game_id', 'shop_id', 'url'), True),)

# Получаем список url всех игр в зависимости от магазина (all - получаем вообще все игры)
def get_all_shops_games(shop):
    if shop == 'all':
        coda_shop = GameUrl.select(GameUrl.game_id, Game.name).join(Game).where(GameUrl.shop_id==1)
        seagm_shop = GameUrl.select(GameUrl.game_id, Game.name).join(Game).where(GameUrl.shop_id==2)
        return coda_shop.intersect(seagm_shop).dicts()
    elif shop == 'Codashop':
        return GameUrl.select(GameUrl.game_id, Game.name).join(Game).where(GameUrl.shop_id==1).dicts()
    elif shop == 'SEAGM':
        return GameUrl.select(GameUrl.game_id, Game.name).join(Game).where(GameUrl.shop_id==2).dicts()
    else:
        pass

def get_game_info(game_id, region_code):
    game_name = ''
    last_updated = ''
    codashop_url = ''
    seagm_url = ''
    try:
        game_name = Game.get(id=game_id).name
        last_updated = GameAddon.select(fn.MAX(GameAddon.updated)).where(GameAddon.game_id==game_id, GameAddon.region==region_code).scalar()
        codashop_url = GameUrl.get(shop_id=1, game_id=game_id).url
        seagm_url = GameUrl.get(shop_id=2, game_id=game_id).url
    except GameUrl.DoesNotExist:
        pass
    return game_name, last_updated, codashop_url, seagm_url

def get_addons(game_id, region_code):
    try:
        addons_list = [i.name for i in GameAddon.select(GameAddon.name).distinct().where(GameAddon.game_id==game_id, GameAddon.region==region_code)]
        message_text = ''
        for addon in addons_list:
            message_text = message_text + f'<b>{addon}:</b>\n'
            for b in GameAddon.select(GameAddon.price, GameAddon.currency, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel).where(GameAddon.name==addon, GameAddon.game_id==game_id, GameAddon.region==region_code):
                message_text = message_text + f'{b.price} {b.currency}, {b.payment_channel_id.name}, {b.shop_id.name}\n'
    except GameUrl.DoesNotExist:
        message_text = 'Отсутствует такая игра в БД'
        pass
    print(message_text)
    return message_text

# Забираем все данные из таблицы gameaddon, пишем в csv файл
def get_csv_data():
    b = GameAddon.select(
        Game.name.alias('Game Name'), 
        GameAddon.name.alias('Addon Name'), 
        GameAddon.price.alias('Price'), 
        GameAddon.currency.alias('Currency'), 
        GameAddon.region_id.alias('Region'), 
        PaymentChannel.name.alias('Payment Channel'), 
        Shop.name.alias('Shop'),
        GameAddon.updated.alias('Last Updated')
    ).join(Shop).switch(GameAddon).join(PaymentChannel).switch(GameAddon).join(Game).dicts().execute()
    with open('game_addon_data.csv', 'w', newline='') as out:
        headers = list(b[0].keys())
        writer = csv.DictWriter(out, fieldnames=headers)
        writer.writeheader()
        for row in b:
            writer.writerow(row)
 

# print(PaymentChannel.get(PaymentChannel.id == PaymentChannelCode.get(code=1201).paymentchannel_id).id)

#print([i['name'] for i in Shop.select(Shop.name).dicts()])

# print([f'{i.name} : {i.price}, {i.payment_channel_id.name}, {i.shop_id.name}\n' for i in GameAddon.select(GameAddon.name, GameAddon.price, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel)])

# for i in GameAddon.select(GameAddon.name.distinct(), GameAddon.price, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel).where(GameAddon.game_id==1):
#     print(i.name, ':', i.price, '_', i.payment_channel_id.name, '-->', i.shop_id.name)
# db.connect()
# db.create_tables([Game, Shop, PaymentChannel, PaymentChannelCode, Region, GameAddon], safe = True)
# db.close()
# for i in GameAddon.select(GameAddon.name, GameAddon.game_id, GameAddon.shop_id.name).join(Shop).dicts():
#     print(i)

# query = GameAddon.select(fn.MAX(GameAddon.updated)).where(GameAddon.game_id==4).scalar()
# print(query)

#Sget_game_info(1)

# for i in Game.select(Game.id):
#     print(i)

# Region.create_table()
# Shop.create_table()
# PaymentChannelCode.drop_table()
# PaymentChannelCode.create_table()
# GameAddon.create_table()
# PaymentChannelCode.create_table()
# GameAddon.drop_table()

# for key, value in payment_codes.items():
#     PaymentChannelCode.create(code=key, paymentchannel_id=value)

# 1,PayPal
# PaymentChannel.create(name='PayPal', codes='754,756,759,760,762')
# 2,Kreditkarte
# PaymentChannel.create(name='Card', codes='1000,1002,1003,1004,1007')
# 3,GiroPay
# PaymentChannel.create(name='GiroPay', codes='900')
# 4,Paysafecard
# PaymentChannel.create(name='Paysafecard', codes='518')
# PaymentChannel.create(name='Codacash', codes='1201')
# PaymentChannel.create(name='iDeal', codes='901')

# pubg = Game.create(name='PUBG')
# coda = Shop.create(name='Codashop', url='https://codashop.com')
# seagm = Shop.create(name='SEAGM', url='https://www.seagm.com')
# Region.create(code='gb', country = 'Great Britain')
# , 'Kreditkarte', 'GiroPay', 'Paysafecard'

# for key, value in seagm_url_dict.items():
#     #Game.create(name=key)
#     print(key)
#     current_game = Game.get(Game.name == key)
#     print(current_game.id)
#     GameUrl.create(game_id=current_game.id, shop_id = 2, url = value)
#     print(current_game.id, key, value)

# for key in seagm_url_dict.keys():
#     Game.create(name=key)

# current_game = Game.get(Game.id == 1)
# print(GameUrl.get(game_id=current_game.id).url)

# query = Game.select().where(Game.id < 10).limit(100).order_by(Game.id.asc()).execute()
# for i in query:
#     print(i)
# games_selected = query.dicts().execute()
# for game in games_selected:
#     print(game['name'])


# game = Game(name='PUBG')
# game.id=1
# game.save()

# GameAddon.replace(name = '100 + 25 Diamonds', 
#     game_id = 3, 
#     shop_id = 1, 
#     payment_channel_id = 3,
#     price = 1.2,  
#     currency = 'EUR').execute()



# abs = GameUrl.select().join(Game).where(Game.id == 2)
# for i in abs:
#     print(i.game_id, i.shop_id, i.url)

print([i.id for i in Game.select().order_by(Game.updated_date.asc())])