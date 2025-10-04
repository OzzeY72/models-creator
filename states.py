from aiogram.fsm.state import State, StatesGroup

class CreateMaster(StatesGroup):
  agency_type = State()
  agency_id = State()
  type = State()
  name = State()
  age = State()
  phonenumber = State()
  address = State()
  height = State()
  weight = State()
  cupsize = State()
  bodytype = State()
  price_1h = State()
  price_2h = State()
  price_full_day = State()
  photo = State()

class EditMaster(StatesGroup):
  view = State()
  field = State()  
  value = State()

class CreateAgencySpa(StatesGroup):
  name = State()
  phone = State()
  address = State()
  photos = State()