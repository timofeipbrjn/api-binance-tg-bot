from aiogram.fsm.state import StatesGroup, State

class GetCurSteps(StatesGroup):
    first_currency = State()
    second_currency = State()

class InputCur(StatesGroup):
    symbol = State()
