# Бот-парсер сайтов для сравнения цен
# t.me/coda_parser_bot

import seagm_parser as seagm, codashop_parser as coda, secret, re
from aiogram import Bot, Dispatcher, executor, types 
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import time

# Формируем инлайн кнопки
CODA_BTN = InlineKeyboardButton('Codashop', callback_data='coda')
SEAGM_BTN = InlineKeyboardButton('SEAGM', callback_data='seagm')
MAIN_MENU_BTNS = InlineKeyboardMarkup(row_width=2).add(CODA_BTN, SEAGM_BTN)

SEAGM_GAMES_BUTTON = types.InlineKeyboardMarkup(row_width=2)
seagm_button_list = [types.InlineKeyboardButton(text=re.split(r'_seagm', key)[0], callback_data=key) for key in seagm.seagm_url_dict.keys()]
SEAGM_GAMES_BUTTON.add(*seagm_button_list)

CODA_GAMES_BUTTON = types.InlineKeyboardMarkup(row_width=2)
coda_button_list = [types.InlineKeyboardButton(text = re.split(r'_coda', key)[0], callback_data=key) for key in coda.coda_url_dict.keys()]
CODA_GAMES_BUTTON.add(*coda_button_list)

# Функция, обрабатывающая команду /start
async def start(message: types.Message):
    await message.answer(text='Приветики! Выбери, что будем парсить:',
                         reply_markup=MAIN_MENU_BTNS)

# Хендлер для построения меню кнопок
async def games_menu(callback_query: types.CallbackQuery):
    if callback_query.data == 'coda':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text='Список игр, доступных для парсинга через codashop:', reply_markup=CODA_GAMES_BUTTON)
    elif callback_query.data == 'seagm':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text='Список игр, доступных для парсинга через SEAGM:', reply_markup=SEAGM_GAMES_BUTTON)

# Хэндлер коллбэка для инлайн-кнопки игр CODASHOP
async def coda_games_data(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    coda.get_codashop_data(str(callback_query.data))
    print(callback_query.data)
    await bot.send_message(
        callback_query.from_user.id,
        text=coda.codashop_parse(str(callback_query.data)),
        reply_markup=MAIN_MENU_BTNS)

# Хэндлер коллбэка для инлайн-кнопки игр SEAGM
async def seagm_games_data(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    seagm.get_html_content(str(callback_query.data))
    print(callback_query.data)
    await bot.send_message(
        callback_query.from_user.id,
        text=seagm.seagm_parse(str(callback_query.data)),
        reply_markup=MAIN_MENU_BTNS)

# Запускаем бота
if __name__ == '__main__':
    bot = Bot(token=secret.API_KEY)
    dp = Dispatcher(bot)
    dp.register_message_handler(start, commands='start')
    dp.register_callback_query_handler(games_menu, text=['coda', 'seagm'])
    dp.register_callback_query_handler(coda_games_data, text=coda.coda_url_dict.keys())
    dp.register_callback_query_handler(seagm_games_data, text=seagm.seagm_url_dict.keys())
    executor.start_polling(dp, skip_updates=True)
    