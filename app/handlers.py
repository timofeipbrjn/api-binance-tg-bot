from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
import app.keyboards as kb
from services.api_client import CurrencyApiClient
from services.sessions import GetCurSteps
from aiogram.fsm.context import FSMContext

router = Router()

url = 'https://api.binance.com/api/v3/ticker/price'
client = CurrencyApiClient(url)

@router.message(Command('start'))
async def cmd_start(msg: Message):
    user = msg.from_user.first_name or msg.from_user.username if msg.from_user else "User"
    await msg.answer(f"Привет, {user}",
                    reply_markup=kb.main)

@router.message(Command('help'))
async def cmd_help(msg: Message):
    await msg.answer('''
/start
/help
''')

@router.message(Command('about'))
async def cmd_about(msg: Message):
    await msg.answer('''
Бот для получения актуальной информации по курсам валют.
Используемые технологии:
1. Binance
2. Фреймворк aiogram, серверный клиент aiohttp
3. База данных PostgreSQL
''',
reply_markup=kb.links)

@router.message(F.text == 'Курсы валют')
async def currency(msg: Message, state: FSMContext):
    await state.set_state(GetCurSteps.first_currency)
    await msg.answer('Выберите первую валюту:',
                     reply_markup=kb.currency_choice)

@router.message(GetCurSteps.first_currency)
async def get_first_currency(msg: Message, state: FSMContext):
    await state.update_data(first_currency=msg.text)
    await msg.answer(f"Вы выбрали {msg.text} первой валютой, выберите вторую валюту:",
                     reply_markup=kb.currency_choice)
    await state.set_state(GetCurSteps.second_currency)

@router.message(GetCurSteps.second_currency)
async def get_second_currency(msg: Message, state: FSMContext):
    await state.update_data(second_currency=msg.text)
    data = await client.get_data(symbol="BTCUSDT")
    await msg.answer(f'''
Вы выбрали {msg.text} второй валютой, текущий курс:
{data['price']}
''')
