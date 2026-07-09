import time
import asyncpg
import traceback
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from services.api_client import CurrencyApiClient
from services.sessions import GetCurSteps, InputCur

router = Router()

url = 'https://api.binance.com/api/v3/ticker/price'

@router.message(Command('start'))
async def cmd_start(msg: Message, db_pool: asyncpg.Pool):
    user = msg.from_user.first_name or msg.from_user.username if msg.from_user else "User"

    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (tg_id, username)
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO NOTHING
                """,
                msg.from_user.id, msg.from_user.username      
            )
    except Exception:
        print("Execute trouble")
    await msg.answer(f"Привет, {user}",
                    reply_markup=kb.main)


@router.message(F.text == "Назад в меню")
@router.message(Command("cancel"))
async def cancel_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await msg.answer("Главное меню", reply_markup=kb.main)
        return

    await state.clear()
    await msg.answer("Действие отменено. Вы вернулись в главное меню", 
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
/history - история операций
/cancel - отмена действия и возврат в меню
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
    await msg.answer("@fuxx33")

@router.callback_query(F.data == "cancel_fsm")
async def cancel_fsm(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Ввод отменен")
    await callback.message.answer("Вы вернулись в главное меню", 
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
async def get_second_currency(msg: Message, state: FSMContext, client: CurrencyApiClient, db_pool:asyncpg.Pool):
    start = time.perf_counter()
    await state.update_data(second_currency=msg.text)
    data = await state.get_data()
    first_cur = kb.CRYPTO[data.get("first_currency")]
    second_cur = kb.CRYPTO2[data.get("second_currency")]
    try:
        symbol = first_cur + second_cur
        price = await client.get_data(symbol=symbol)
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO query_history (tg_id, ticker, price)
                    VALUES ($1, $2, $3)
                    """,
                    msg.from_user.id, symbol, float(price)
                )
        except Exception as db_err:
            print(f"Ошибка записи истории токена в БД: {db_err}")


        end = time.perf_counter()
        text = f"💎 1 {first_cur} = {price} {second_cur}"
        await msg.answer(f"Вы выбрали {msg.text} целевой валютой.\n{text}")
    except ValueError:
        await msg.answer("Ошибка сервера")
    except Exception as e:
        traceback.print_exc()
        await msg.answer("Произошла техническая ошибка, попробуйте позже.")
    finally:
        await state.clear()
        await msg.answer("Вы вернулись в главное меню",
            reply_markup=kb.main)
        end = time.perf_counter()
        print(f'Скорость: {end - start}')

@router.message(Command('universal_converter'))
@router.message(F.text == "Перевод по токену")
async def universal_converter(msg: Message, state: FSMContext):
    await state.set_state(InputCur.symbol)
    await msg.answer("Введите тикер",
                     reply_markup=kb.main)

@router.message(InputCur.symbol)
async def get_currency_by_token(msg: Message, client: CurrencyApiClient, db_pool:asyncpg.Pool, state: FSMContext):
    try:
        if not msg.text:
            await msg.answer("Тикер не найден",
                             reply_markup=kb.main)
            return

        curs = msg.text.split()
        
        if len(curs) != 2:
            await msg.answer("Неверный формат, введите две валюты через пробел, например: BTC USDT",
                             reply_markup=kb.main)
            return

        first_cur = curs[0]
        second_cur = curs[1]
        symbol = first_cur + second_cur
        price = await client.get_data(symbol=symbol)

        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO query_history (tg_id, ticker, price)
                    VALUES ($1, $2, $3)
                    """,
                    msg.from_user.id, symbol, float(price)
                )
        except Exception as db_err:
            await msg.answer(f"Ошибка записи истории токена в БД: {db_err}")

        text = f"💎 1 {first_cur} = {price} {second_cur}"
        await msg.answer(text, reply_markup=kb.main)

    except ValueError:
        await msg.answer("Ошибка сервера API, попробуйте снова",
                         reply_markup=kb.main)
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        await msg.answer("Такого токена не существует.",
                         reply_markup=kb.main)
        
    finally:
        await state.clear()


@router.message(Command('story'))
@router.message(F.text == "История операций")
async def get_history(msg: Message, db_pool:asyncpg.Pool):
    try:
        async with db_pool.acquire() as conn:
            tickers = await conn.fetch(
                """
                SELECT ticker, price, quiried_at FROM query_history WHERE tg_id=$1
                ORDER BY quiried_at desc LIMIT 5
                """,
                msg.from_user.id
            )
    except Exception as db_err:
        print(f"Ошибка записи истории токена в БД: {db_err}")
        await msg.answer("Не удалось загрузить историю.")
        return
    
    if not tickers:
        await msg.answer("Ваша история запросов пока пуста")
        return
    
    history_text = "📜 Последние 5 запросов: \n"

    for ticker in tickers:
        all_str = f"""
💎 **{ticker["ticker"]}** -> {ticker["price"]:.4f}
⏱ {ticker["quiried_at"].strftime("%d.%m %H:%M")}
        """
        history_text += all_str
    
    await msg.answer(history_text)
