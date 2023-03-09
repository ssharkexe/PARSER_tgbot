import dbdata as db
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

region_button = InlineKeyboardButton('🌍 Регион', callback_data='reg_settings')
csv_export_button = InlineKeyboardButton('📝 Скачать в CSV', callback_data='csv_export')

# инлайн клавиатура конкретной игры, кнопки "показать аддоны/обновить/назад"
def make_inline_keyboard(row_width, game_id, region_code):
    addons_callback_text = f'addons_{game_id}_{region_code}'
    update_callback_text = f'update_{game_id}_{region_code}'
    back_button = InlineKeyboardButton('↩️ Назад', callback_data=f'back_{region_code}')
    show_addons = InlineKeyboardButton(text = 'Аддоны', callback_data=addons_callback_text)
    update_data = InlineKeyboardButton(text = 'Обновить', callback_data=update_callback_text)
    if row_width == 3:
        INGAME_BUTTON = InlineKeyboardMarkup(row_width=3)
        INGAME_BUTTON.add(show_addons, update_data, back_button)
    elif row_width == 2:
        INGAME_BUTTON = InlineKeyboardMarkup(row_width=2)
        INGAME_BUTTON.add(update_data, back_button)
    else:
        pass
    return INGAME_BUTTON

# инлайн клавиатура со списком игр в зависимости от выбранного магазина
def list_of_games_kb(shop, region_code):
    GAMES_LIST_KB = InlineKeyboardMarkup(row_width=2)
    back_button = InlineKeyboardButton('↩️ Назад', callback_data=f'back_{region_code}')
    buttons_list = [InlineKeyboardButton(text = i['name'], callback_data='game_' + str(i['game_id']) + '_' + region_code) for i in db.get_all_shops_games(shop)]
    GAMES_LIST_KB.add(*buttons_list, region_button, back_button)
    return GAMES_LIST_KB

# инлайн клавиатура со списком игры в обоих магазинах + кнопки магазинов
def list_of_all_shop_games_kb(region_code):
    ALL_SHOP_GAMES_KB = InlineKeyboardMarkup(row_width=2)
    shop_list = [InlineKeyboardButton(text = '🛒 ' + i['name'], callback_data=i['name'] + '_' + region_code) for i in db.Shop.select(db.Shop.id, db.Shop.name).dicts()]
    button_list = [InlineKeyboardButton(text = i['name'], callback_data='game_' + str(i['game_id']) + '_' + region_code) for i in db.get_all_shops_games('all')]
    ALL_SHOP_GAMES_KB.add(*shop_list, *button_list, region_button, csv_export_button)
    return ALL_SHOP_GAMES_KB

# инлайн клавиатура со списком регионов
def regions_kb():
    REGIONS_LIST_KB = InlineKeyboardMarkup(row_width=2)
    buttons_list = [InlineKeyboardButton(text = i['country'], callback_data='region_' + i['code']) for i in db.Region.select(db.Region.code, db.Region.country).dicts()]
    REGIONS_LIST_KB.add(*buttons_list)
    return REGIONS_LIST_KB