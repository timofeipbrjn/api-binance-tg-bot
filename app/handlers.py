from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from services.api_client import CurrencyApiClient
from services.sessions import GetCurSteps
import time

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

@router.message(F.text == "Назад в меню")
async def back_to_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Вы вернулись в главное меню",
                 reply_markup=kb.main)

@router.message(F.text == 'Курсы валют')
async def currency(msg: Message, state: FSMContext):
    await state.set_state(GetCurSteps.first_currency)
    await msg.answer('Выберите первую валюту:',
                     reply_markup=kb.currency_choice)

@router.message(GetCurSteps.first_currency)
async def get_first_currency(msg: Message, state: FSMContext):
    await state.update_data(first_currency=msg.text)
    await msg.answer(f"Вы выбрали {msg.text}, выберите целевую валюту:",
                     reply_markup=kb.currency_choice2)
    await state.set_state(GetCurSteps.second_currency)

@router.message(GetCurSteps.second_currency)
async def get_second_currency(msg: Message, state: FSMContext):
    start = time.perf_counter()
    await state.update_data(second_currency=msg.text)
    start = time.perf_counter()
    data = await state.get_data()
    first_cur = kb.CRYPTO[data.get("first_currency")]
    second_cur = kb.CRYPTO2[data.get("second_currency")]
    try:
        symbol = first_cur + second_cur
        data = await client.get_data(symbol=symbol)
        price = data['price']
        price = str(price).rstrip("0").rstrip(".")
        end = time.perf_counter()
        text = f"💎 1 {first_cur} = {price} {second_cur}"
        await msg.answer(f"Вы выбрали {msg.text} второй валютой.\n{text}")
    except ValueError:
        await msg.answer("Ошибка сервера API")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        await msg.answer("Произошла техническая ошибка, попробуйте позже.")
    finally:
        await state.clear()
        await back_to_menu(msg, state)
        end = time.perf_counter()
        print(f'Скорость: {end - start}')
