from peewee import *
import datetime, csv
from peewee import DoesNotExist

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

def get_game_info(game_id: int, region_code: str) -> tuple:
    game_name = ''
    last_updated = ''
    codashop_url = ''
    seagm_url = ''
    try:
        game_name = Game.get(id=game_id).name
        # Смотрим список сохраненных цен на аддоны и выбираем посленее по дате (fn.MAX)
        last_updated = GameAddon.select(fn.MAX(GameAddon.updated)).where(GameAddon.game_id==game_id, GameAddon.region==region_code).scalar()
        codashop_url = GameUrl.get(shop_id=1, game_id=game_id).url
        seagm_url = GameUrl.get(shop_id=2, game_id=game_id).url
        # print(seagm_url, codashop_url)
    except DoesNotExist:
        print('Такого урла нет')
        pass
    return game_name, last_updated, codashop_url, seagm_url

def get_addons(game_id, region_code) -> str:
    try:
        addons_list = [i.name for i in GameAddon.select(GameAddon.name).distinct().where(GameAddon.game_id==game_id, GameAddon.region==region_code)]
        message_text = ''
        for addon in addons_list:
            message_text = message_text + f'<b>{addon}:</b>\n'
            for b in GameAddon.select(GameAddon.price, GameAddon.currency, PaymentChannel.name, Shop.name).join(Shop).switch(GameAddon).join(PaymentChannel).where(GameAddon.name==addon, GameAddon.game_id==game_id, GameAddon.region==region_code):
                message_text = message_text + f'{b.price} {b.currency}, {b.payment_channel_id.name}, {b.shop_id.name}\n'
    except DoesNotExist:
        message_text = 'Отсутствует такая игра в БД'
        pass
    print(message_text)
    return message_text

# Забираем все данные из таблицы gameaddon, пишем в csv файл
def get_csv_data() -> None:
    b = GameAddon.select(
        Game.name.alias('Game Name'), 
        GameAddon.name.alias('Addon Name'), 
        GameAddon.price.alias('Price'), 
        GameAddon.currency.alias('Currency'), 
        GameAddon.region.alias('Region'), 
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