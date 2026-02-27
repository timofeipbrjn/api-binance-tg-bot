from aiogram.fsm.state import StatesGroup, State

class GetCurSteps(StatesGroup):
    step = State()
    first_currency = State()
    second_currency = State()
