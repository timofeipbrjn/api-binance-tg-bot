from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

CRYPTO = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Binance coin': 'BNB',
    'Doge': 'DOGE',
    'Dollar': 'USDT',
    'Euro': 'EUR',
    'Pound': 'GBP',
    'Lira': 'TRY'
}

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Курсы валют'), KeyboardButton(text='придумать чота с дб')],
    [KeyboardButton(text='Доступные команды'), KeyboardButton(text='Обратная связь')],
    [KeyboardButton(text='О боте')]
],
                        resize_keyboard=True,
                        input_field_placeholder='Начальное меню')

links = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Binance', url='https://www.binance.com/en')],
    [InlineKeyboardButton(text='aiogram', url='https://aiogram.dev'), InlineKeyboardButton(text='iohttp', url='https://docs.aiohttp.org/en/stable/')],
    [InlineKeyboardButton(text='Database', url='https://www.postgresql.org')]
])

currency_choice = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=list(CRYPTO.keys())[0]), KeyboardButton(text=list(CRYPTO.keys())[4])],
    [KeyboardButton(text=list(CRYPTO.keys())[1]), KeyboardButton(text=list(CRYPTO.keys())[5])],
    [KeyboardButton(text=list(CRYPTO.keys())[2]), KeyboardButton(text=list(CRYPTO.keys())[6])],
    [KeyboardButton(text=list(CRYPTO.keys())[3]), KeyboardButton(text=list(CRYPTO.keys())[7])]
])
