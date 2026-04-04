from email import message
from encodings.rot_13 import rot13

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from services.api_client import CurrencyApiClient
from services.sessions import GetCurSteps, InputCur
import time

router = Router()

url = 'https://api.binance.com/api/v3/ticker/price'

@router.message(Command('start'))
async def cmd_start(msg: Message):
    user = msg.from_user.first_name or msg.from_user.username if msg.from_user else "User"
    await msg.answer(f"Привет, {user}",
                    reply_markup=kb.main)

@router.message(F.text == "Доступные команды")
@router.message(Command('help'))
async def cmd_help(msg: Message):
    await msg.answer('''
/start - запуск бота
/about - о боте
/help - доступные команды
/story - история запросов
/contact - контакт разработчика
''')

@router.message(F.text == "О боте")
@router.message(Command('about'))
async def cmd_about(msg: Message):
    await msg.answer('''
🤖 Помощь по работе с ботом
Я — твой персональный ассистент для мониторинга курсов валют в реальном времени, использующий данные биржи Binance.

📋 Основные функции:

💱 Базовые валюты — Мгновенная конвертация самых популярных мировых валют и криптоактивов в два клика. Просто выбери нужный раздел в главном меню. /base_converter

🪙 Перевод по токену — Гибкий поиск курсов любых торговых пар, доступных на Binance. Просто введи тикер токена (например, BTC, ETH, SOL). /universal_converter

📜 История — Список твоих последних операций для быстрого повторного доступа к нужным парам. /story
''')

@router.message(F.text == "Обратная связь")
@router.message(Command('contact'))
async def contact(msg:Message):
    await msg.answer("@iiiooyyyyyyy")

@router.message(F.text == "Назад в меню")
async def back_to_menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Вы вернулись в главное меню",
                 reply_markup=kb.main)

@router.message(Command('base_converter'))
@router.message(F.text == 'Базовые валюты')
async def base_converter(msg: Message, state: FSMContext):
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
async def get_second_currency(msg: Message, state: FSMContext, client: CurrencyApiClient):
    start = time.perf_counter()
    await state.update_data(second_currency=msg.text)
    data = await state.get_data()
    first_cur = kb.CRYPTO[data.get("first_currency")]
    second_cur = kb.CRYPTO2[data.get("second_currency")]
    try:
        symbol = first_cur + second_cur
        price = await client.get_data(symbol=symbol)
        end = time.perf_counter()
        text = f"💎 1 {first_cur} = {price} {second_cur}"
        await msg.answer(f"Вы выбрали {msg.text} целевой валютой.\n{text}")
    except ValueError:
        await msg.answer("Ошибка сервера")
    except Exception as e:
        print(f"ошибка: {e}")
        await msg.answer("Произошла техническая ошибка, попробуйте позже.")
    finally:
        await state.clear()
        await back_to_menu(msg, state)
        end = time.perf_counter()
        print(f'Скорость: {end - start}')

@router.message(Command('universal_converter'))
@router.message(F.text == "Перевод по токену")
async def universal_converter(msg: Message, state: FSMContext):
    await msg.answer("Введите токен формата: BTC USDT (токен первой валюты [пробел] токен второй валюты)",
                     reply_markup=kb.back_menu)
    await state.set_state(InputCur.symbol)

@router.message(InputCur.symbol)
async def get_currency_by_token(msg: Message, client: CurrencyApiClient):
    try:
        if msg.text:
            curs = msg.text.split()
        else:
            print("Нет токена")
            return
        first_cur = curs[0]
        second_cur = curs[1]
        symbol = first_cur + second_cur
        price = await client.get_data(symbol=symbol)
        text = f"💎 1 {first_cur} = {price} {second_cur}"
        await msg.answer(text, reply_markup=kb.back_menu)
    except ValueError:
        await msg.answer("Ошибка сервера API, попробуйте снова",
                         reply_markup=kb.back_menu)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        await msg.answer("Такого токена не существует.",
                         reply_markup=kb.back_menu)
