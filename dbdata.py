from peewee import *
import datetime

# Создаем соединение с нашей базой данных
# В нашем примере у нас это просто файл базы
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

class GameAddon(BaseModel):
    id = AutoField(primary_key = True)
    name = CharField(null=False)
    game_id = ForeignKeyField(Game, backref='addons')
    shop_id = ForeignKeyField(Shop)
    payment_channel_id = ForeignKeyField(PaymentChannel)
    price = FloatField(null=False)
    currency = CharField(null=False)
    updated = DateTimeField(default = datetime.datetime.now)

    class Meta:
        indexes = (
            # create a unique on name/game/shop/payment
            (('name', 'game_id', 'shop_id', 'payment_channel_id'), True),)

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

def get_game_info(game_id):
    game_name = ''
    last_updated = ''
    codashop_url = ''
    seagm_url = ''
    try:
        game_name = Game.get(id=game_id).name
        last_updated = GameAddon.select(fn.MAX(GameAddon.updated)).where(GameAddon.game_id==game_id).scalar()
        codashop_url = GameUrl.get(shop_id=1, game_id=game_id).url
        seagm_url = GameUrl.get(shop_id=2, game_id=game_id).url
    except GameUrl.DoesNotExist:
        pass
    return game_name, last_updated, codashop_url, seagm_url



def get_addons(game_id):
    try:
        addons_list = [i.name for i in GameAddon.select(GameAddon.name).distinct().where(GameAddon.game_id==game_id)]
        message_text = ''
        for addon in addons_list:
            message_text = message_text + f'<b>{addon}:</b>\n'
            for b in GameAddon.select(GameAddon.price, GameAddon.currency, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel).where(GameAddon.name==addon, GameAddon.game_id==game_id):
                message_text = message_text + f'{b.price} {b.currency}, {b.payment_channel_id.name}, {b.shop_id.name}\n'
    except GameUrl.DoesNotExist:
        pass
    print(message_text)
    return message_text

#print([i['name'] for i in Shop.select(Shop.name).dicts()])

# print(get_addons(10))

# print([f'{i.name} : {i.price}, {i.payment_channel_id.name}, {i.shop_id.name}\n' for i in GameAddon.select(GameAddon.name, GameAddon.price, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel)])

# for i in GameAddon.select(GameAddon.name.distinct(), GameAddon.price, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel).where(GameAddon.game_id==1):
#     print(i.name, ':', i.price, '_', i.payment_channel_id.name, '-->', i.shop_id.name)

# for i in GameAddon.select(GameAddon.name, GameAddon.game_id, GameAddon.shop_id.name).join(Shop).dicts():
#     print(i)

# query = GameAddon.select(fn.MAX(GameAddon.updated)).where(GameAddon.game_id==4).scalar()
# print(query)

#Sget_game_info(1)

# for i in Game.select(Game.id):
#     print(i)

# Game.create_table()
# Shop.create_table()
# PaymentChannel.create_table()
# GameAddon.create_table()
# GameUrl.create_table()
# GameUrl.drop_table()

# pubg = Game.create(name='PUBG')
# coda = Shop.create(name='Codashop', url='https://codashop.com')
# seagm = Shop.create(name='SEAGM', url='https://www.seagm.com')
# GameUrl.create(game_id=1, shop_id = 2, url = 'https://www.seagm.com/fr/pubg-mobile')
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

# query = Game.select().where(Game.id < 10).limit(100).order_by(Game.id.asc())
# print(query)
# games_selected = query.dicts().execute()
# for game in games_selected:
#     print(game['name'])


#print(PaymentChannel.get(PaymentChannel.name == '325 UC').id)
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