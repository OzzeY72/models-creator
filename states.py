from aiogram.fsm.state import State, StatesGroup

class CreateMaster(StatesGroup):
    name = State()
    age = State()
    phonenumber = State()
    address = State()
    height = State()
    weight = State()
    cupsize = State()
    clothsize = State()
    price_1h = State()
    price_2h = State()
    price_full_day = State()
    photo = State()
