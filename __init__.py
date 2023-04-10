# Бот-парсер сайтов для сравнения цен
# codashop.com и seagm.com
# t.me/coda_parser_bot

import seagm_parser as seagm, codashop_parser as coda, secret, re, json, dbdata as db, buttons as kb, asyncio, random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import time
from aiogram.utils.exceptions import NetworkError
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import NetworkError
from asyncio.exceptions import TimeoutError
from aiohttp.client_exceptions import ClientConnectorError
from asyncio import sleep

class GameAddonsMenu(StatesGroup):
    choosing_addon = State()

bot = Bot(token=secret.API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Функция, обрабатывающая команду /start
async def start(message: types.Message):
    region_code = 'es'
    await message.answer(text="""Привет! Я немного обновился, теперь сохраняю все данные в SQL-базу.\n
Вот список игр, по которым я могу выгрузить данные c SEAGM и Codashop. Или можешь выбрать магазин и посмотреть все игры из него.\n
Регион по умолчанию - Испания (Spain, es), его можно изменить в настройках ниже""",
                         reply_markup=kb.list_of_all_shop_games_kb(region_code))
    state = Dispatcher.get_current().current_state()
    await state.finish()

# Хендлер для возврата в главное меню
async def back_to_main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup()
    # await bot.answer_callback_query(callback_query.id)
    region_code = callback_query.data.split('_')[-1]
    country = db.Region.get(code=region_code).country
    print(region_code)
    await bot.send_message(
        callback_query.from_user.id, 
        text=f'Главное меню.\nРегион <b>{country}</b>', 
        parse_mode='HTML', 
        reply_markup=kb.list_of_all_shop_games_kb(region_code))
    state = Dispatcher.get_current().current_state()
    await state.finish()

# Хендлер для построения меню кнопок
async def games_menu(callback_query: types.CallbackQuery):
    shop = callback_query.data.split('_')[0]
    region_code = callback_query.data.split('_')[-1]
    country = db.Region.get(code=region_code).country
    await callback_query.message.delete()
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id, 
        text=f'Список игр, доступных для парсинга через {shop}\nРегион <b>{country}</b>', 
        parse_mode='HTML', 
        reply_markup=kb.list_of_games_kb(shop, region_code))

# Хэндлер меню игры
async def game_menu(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    # await callback_query.message.edit_reply_markup()
    await bot.answer_callback_query(callback_query.id)
    game_id = int(callback_query.data.split('_')[-2])
    region_code = callback_query.data.split('_')[-1]
    country = db.Region.get(code=region_code).country
    game_data = db.get_game_info(game_id, region_code)
    game_name = game_data[0]
    last_updated = game_data[1]
    # -------Сохраняем атрибуты в машину состояний
    # await ShowAddons.game.set()
    # state = Dispatcher.get_current().current_state()
    # await state.update_data(game_id=game_id, game_name=game_name, coda_url=game_data[2], seagm_url=game_data[3]) # сохраняем в память FSM id, name, url игры
    # -------
    if game_data[2] == '':
        codashop = '❌'
    else:
        codashop = '✅'
    if game_data[3] == '':
        seagm = '❌'
    else:
        seagm = '✅'
    try:
        await bot.send_message(
            callback_query.from_user.id,
            text=f'<b>{game_name}</b>\nОбновлено:\n{last_updated:%d.%m.%Y %H:%M}\n{codashop} Codashop\n{seagm} SEAGM\nРегион <b>{country}</b>', parse_mode='HTML',
            reply_markup=kb.make_inline_keyboard(3, game_id, region_code))
    except TypeError:
        await bot.send_message(
            callback_query.from_user.id,
            text=f'<b>{game_name}</b>\nОбновлено:\n❌\n{codashop} Codashop\n{seagm} SEAGM\nРегион <b>{country}</b>', parse_mode='HTML',
            reply_markup=kb.make_inline_keyboard(2, game_id, region_code))

# Хэндлер коллбэка для обновление данных в базе
async def update_games_data(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup()
    game_id = int(callback_query.data.split('_')[-2])
    region_code = callback_query.data.split('_')[-1]
    await bot.answer_callback_query(callback_query.id)
    data_coda = coda.get_codashop_data(game_id=game_id, shop_id=1, region_code=region_code)
    data_seagm = seagm.get_seagm_data(game_id=game_id, shop_id=2, region_code=region_code)
    try:
        updated_text = f'{data_coda}\n{data_seagm}\n{db.get_game_info(game_id, region_code)[1]:%d.%m.%Y %H:%M}'
        await bot.send_message(
            callback_query.from_user.id,
            text=updated_text,
            reply_markup=kb.make_inline_keyboard(3, game_id, region_code))
    except TypeError:
        updated_text = f'{data_coda}\n{data_seagm}'
        await bot.send_message(
            callback_query.from_user.id,
            text=updated_text,
            reply_markup=kb.make_inline_keyboard(2, game_id, region_code))


# # Хэндлер коллбэка для инлайн-кнопки игр SEAGM
# async def seagm_games_data(callback_query: types.CallbackQuery):
#     await callback_query.message.delete()
#     #await callback_query.message.edit_reply_markup()
#     await bot.answer_callback_query(callback_query.id)
#     seagm.get_html_content(str(callback_query.data))
#     params = seagm.seagm_parse(str(callback_query.data))
#     if isinstance(params, (list, tuple)):
#         #print(params)
#         await GameAddonsMenu.choosing_addon.set()
#         state = Dispatcher.get_current().current_state()
#         print(state)
#         await state.update_data(name_list=params[0], url_list=params[1], game=str(callback_query.data)) # сохраняем в память FSM список аддонов, список url и название самой игры
#         SEAGM_GIFTCARD_BTN = InlineKeyboardMarkup(row_width=1) 
#         seagm_giftcard_list = [InlineKeyboardButton(text = name, callback_data = name) for name, url in zip(params[0], params[1])] # формируем перечень из разделов с аддонами
#         #print(seagm_giftcard_list)
#         SEAGM_GIFTCARD_BTN.add(*seagm_giftcard_list)
#         await bot.send_message(
#             callback_query.from_user.id,
#             text='У игры есть несколько разделов по продаже аддонов:',
#             reply_markup=SEAGM_GIFTCARD_BTN)
#     #print(callback_query.data)
#     else:
#         await bot.send_message(
#             callback_query.from_user.id,
#             text=seagm.seagm_parse(str(callback_query.data)),
#             reply_markup=MAIN_MENU_BTNS)

# # Хэндлер коллбэка для инлайн-кнопки гифткарт SEAGM
# async def seagm_giftcards_data(callback_query: types.CallbackQuery, state: FSMContext):
#     await callback_query.message.delete()
#     #await callback_query.message.edit_reply_markup() # или удаление сообщения целиком, или скрытие inline кнопок
#     data = await state.get_data()
#     await bot.send_message(
#             callback_query.from_user.id,
#             text=seagm.seagm_addon_parse(url=data['url_list'][data['name_list'].index(callback_query.data)], game = callback_query.data),
#             reply_markup=MAIN_MENU_BTNS)
#     await state.finish()

# Хэндлер отображения списка аддонов из базы по конкретной игре
async def show_addons_from_db(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup()
    print(f'В колбэке приходит: {callback_query.data}')
    game_id = callback_query.data.split('_')[-2]
    region_code = callback_query.data.split('_')[-1]
    await bot.send_message(
            callback_query.from_user.id,
            text=db.get_addons(game_id, region_code), parse_mode='HTML',
            reply_markup=kb.make_inline_keyboard(3, game_id, region_code))
    
# Хэндлер выбора региона
async def region_settings(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    print(f'В колбэке выбора региона приходит: {callback_query.data}')
    await bot.send_message(
            callback_query.from_user.id,
            text='Выбери страну:', parse_mode='HTML',
            reply_markup=kb.regions_kb())

# Хэндлер отправки ботом файла со всеми данными 
async def send_csv_data(callback_query: types.CallbackQuery):
  db.get_csv_data()
  with open('game_addon_data.csv', 'rb') as doc:
    await bot.send_document(callback_query.from_user.id, document=doc)

# # Функция декоратора для перезапуска бота через 10 секунд после networkerror (потеря соединения с инетом)
# def NetworkErrorHandler(func):
#     def wrap(*args, **kwargs):
#         while True:
#             try:
#                 func(*args, **kwargs)
#             except NetworkError:
#                 print(f'NetworkError excepted, wait 10 second')
#                 sleep(10)
#             except TimeoutError:
#                 print(f'TimeoutError excepted, wait 10 second')
#                 sleep(10)
#             except ClientConnectorError:
#                 print(f'ClientConnectorError excepted, wait 10 second')
#                 sleep(10)
#     return wrap

# @NetworkErrorHandler


async def endless_parser():
    game_ids = [i.id for i in db.Game.select().order_by(db.Game.updated_date.asc())]
    region_codes = [i.code for i in db.Region.select()]
    while True:
        for game in game_ids:
            for region in region_codes:
                    try:
                        data_coda = coda.get_codashop_data(game_id=game, shop_id=1, region_code=region)
                        data_seagm = seagm.get_seagm_data(game_id=game, shop_id=2, region_code=region)
                        sleeptimer = random.randint(600, 900)
                    except AttributeError:
                        sleeptimer = 1800
                    # print(data_coda)
                    print(f'Обновил данные по игре {game} в регионе {region}. Спим {sleeptimer} секунд')
                    await sleep(sleeptimer)

# Список хэндлеров и запуск бота через отдельную функцию с декоратором ошибки соединения
if __name__ == '__main__':
    dp.register_message_handler(start, commands='start')
    dp.register_callback_query_handler(update_games_data, text_contains='update_')
    dp.register_callback_query_handler(show_addons_from_db, text_contains='addons_')
    dp.register_callback_query_handler(games_menu, lambda msg: any(i['name'] in msg.data for i in db.Shop.select(db.Shop.name).dicts()), state='*')
    dp.register_callback_query_handler(back_to_main_menu, lambda msg: any(i in msg.data for i in ['region_', 'back_']), state='*')
    dp.register_callback_query_handler(region_settings, state='*', text='reg_settings')
    dp.register_callback_query_handler(game_menu, lambda msg: any(i in msg.data for i in [f'game_{i}' for i in db.Game.select(db.Game.id)]))
    dp.register_callback_query_handler(send_csv_data, state='*', text='csv_export')
    loop = asyncio.get_event_loop()
    loop.create_task(endless_parser())
    executor.start_polling(dp, skip_updates=True)
    