from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

CRYPTO = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Binance coin': 'BNB',
    'Doge': 'DOGE',
    'Solana': 'SOL',
    'Cardano': 'ADA'
}

CRYPTO2 = {
    'Dollar(USDT)': 'USDT',
    'Euro': 'EUR',
    'Pound': 'GBP',
    'Lira': 'TRY',
    'Ien': 'JPY',
    'Real': 'BRL'
}

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Базовые валюты'), KeyboardButton(text='Перевод по токену')],
    [KeyboardButton(text='Доступные команды'), KeyboardButton(text='История операций')],
    [KeyboardButton(text='Обратная связь'), KeyboardButton(text='О боте')]
])

currency_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=list(CRYPTO.keys())[0]), KeyboardButton(text=list(CRYPTO.keys())[3])],
    [KeyboardButton(text=list(CRYPTO.keys())[1]), KeyboardButton(text=list(CRYPTO.keys())[4])],
    [KeyboardButton(text=list(CRYPTO.keys())[2]), KeyboardButton(text=list(CRYPTO.keys())[5])],
    [KeyboardButton(text="Назад в меню")]
])

currency_choice2 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=list(CRYPTO2.keys())[0]), KeyboardButton(text=list(CRYPTO2.keys())[3])],
    [KeyboardButton(text=list(CRYPTO2.keys())[1]), KeyboardButton(text=list(CRYPTO2.keys())[4])],
    [KeyboardButton(text=list(CRYPTO2.keys())[2]), KeyboardButton(text=list(CRYPTO2.keys())[5])],
    [KeyboardButton(text="Назад в меню")]
])

back_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Назад в меню")],
],
                    resize_keyboard=True)
