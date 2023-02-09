# Бот-парсер сайтов для сравнения цен
# t.me/coda_parser_bot
# 

import seagm_parser as seagm, codashop_parser as coda, secret
from aiogram import Bot, Dispatcher, executor, types 
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import time




# Формируем инлайн кнопки

CODA_BTN = InlineKeyboardButton('Codashop', callback_data='coda')
SEAGM_BTN = InlineKeyboardButton('SEAGM', callback_data='seagm')
MAIN_MENU_BTNS = InlineKeyboardMarkup().add(CODA_BTN, SEAGM_BTN)

SEAGM_GAMES_BUTTON = types.InlineKeyboardMarkup(resize_keyboard = True)
for key, value in seagm.seagm_url_dict.items():
    SEAGM_GAMES_BUTTON.row(types.InlineKeyboardButton(text=key, callback_data=key))

CODA_GAMES_BUTTON = types.InlineKeyboardMarkup(resize_keyboard = True)
for key, value in coda.coda_url_dict.items():
    CODA_GAMES_BUTTON.row(types.InlineKeyboardButton(text=key, callback_data=key))

#get_html_content(seagm_url_dict['freefire_seagm'])
#get_html_content(seagm_url_dict['legends_seagm'])
#seagm_parse(seagm_url_dict['freefire_seagm'])
#get_html_content(seagm_url_dict['codashop'])
#seagm_parse(seagm_url_dict['pubg_seagm'])
#get_codashop_data(coda_url_dict['coda_pubg'])
#parse_codashop_data(coda_url_dict['coda_pubg'])

#coda.get_codashop_data(coda.coda_url_dict['coda_wwh'])
#coda.parse_codashop_data(coda.coda_url_dict['coda_wwh'])

# Функция формирования меню бота
def build_main_menu(message):
        keyboard=types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True) 
        button_1=types.KeyboardButton(seagm_url_dict.keys[0])
        button_2=types.KeyboardButton(seagm_url_dict.keys[1]) 
        button_3=types.KeyboardButton(seagm_url_dict.keys[2]) 
        keyboard.add(button_1, button_2, button_3)
        dp.send_message(message.chat.id, text='Выбирай, какую игру парсить:', reply_markup = keyboard)

# Функция, обрабатывающая команду /start
async def start(message: types.Message):
    await message.answer(text='Приветики! Выбери, что будем парсить:',
                         reply_markup=MAIN_MENU_BTNS)

# Хендлер для построения меню кнопок
async def games_menu(callback_query: types.CallbackQuery):
    if callback_query.data == 'coda':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text='Список игр, доступных для парсинга через codashop, следующий:', reply_markup=CODA_GAMES_BUTTON)
    elif callback_query.data == 'seagm':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, text='Список игр, доступных для парсинга через SEAGM, следующий:', reply_markup=SEAGM_GAMES_BUTTON)

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
    