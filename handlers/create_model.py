from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import requests
from states import CreateMaster
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
import os
from aiogram import Bot, F
from dotenv import load_dotenv
import tempfile

from utils import format_agencyspa, get_agency_keyboard, preload_image, send_agencies_carousel

load_dotenv()
router = Router()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

agencies_cache = []

async def get_agencies_spa(callback, agencies_type):
    global agencies_cache
    url = f"{API_URL}/agencies"

    if agencies_type == "agency":
        url += "/agencies/"
    else:
        url += "/spa/"

    resp = requests.get(url)
    if resp.status_code != 200:
        await callback.answer(f"❌ Error while fetching {agencies_type}")
        return

    agencies = resp.json()
    agencies_cache = resp.json()

    if not agencies:
        await callback.message.answer(f"📭 No pending {agencies_type}")
        return
    
    return agencies


async def create_model_kb(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👩 Escort", callback_data="create_model")],
        [InlineKeyboardButton(text="🏢 Add to Agency", callback_data="add_to:agency")],
        [InlineKeyboardButton(text="🏖️ Add to SPA", callback_data="add_to:spa")],
    ])
    await message.answer("Choose an option:", reply_markup=kb)

async def choose_model_type(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👩 Regular Escort", callback_data="create_escort:regular")],
        [InlineKeyboardButton(text="🏢 Top Escort", callback_data="create_escort:top")],
    ])
    await message.answer("Choose an option:", reply_markup=kb)

# 2️⃣ Старт процесса
@router.message(F.text == "➕ Add model")
async def start_create_master(message: Message, state: FSMContext):
    await create_model_kb(message, state)

@router.callback_query(F.data.startswith("add_to"))
async def start_create_master_in_agency(callback: CallbackQuery, state: FSMContext):
    _, agency_type = callback.data.split(":")
    await state.update_data(agency_type=agency_type)
    await state.set_state(CreateMaster.agency_id)

    agencies = await get_agencies_spa(callback, agency_type)
    await send_agencies_carousel(callback.message, agencies, state, 0)
    await callback.answer()

async def update_agency_message(callback: CallbackQuery, agency, text, kb, new_index):
    if agency.get("main_photo"):
      photo = await preload_image(agency, API_URL)
      media = InputMediaPhoto(media=photo, caption=text)
      await callback.message.edit_media(media=media, reply_markup=kb)
    else:
      try:
        await callback.message.edit_caption(caption=text, reply_markup=kb)
      except:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("agency_prev"))
async def agency_prev(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(agencies_cache)

    new_index = (current - 1) % total
    agency = agencies_cache[new_index]

    text = format_agencyspa(agency)
    kb = get_agency_keyboard(new_index, total, agency.get("id"))

    await update_agency_message(callback, agency, text, kb, new_index)
    await callback.answer()


@router.callback_query(F.data.startswith("agency_next"))
async def agency_next(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(agencies_cache)

    new_index = (current + 1) % total
    agency = agencies_cache[new_index]

    text = format_agencyspa(agency)
    kb = get_agency_keyboard(new_index, total, agency.get("id"))

    await update_agency_message(callback, agency, text, kb, new_index)
    await callback.answer()


@router.callback_query(F.data.startswith("agency_choose"))
async def start_create_master_in_agency(callback: CallbackQuery, state: FSMContext):
    _, agency_id = callback.data.split(":")
    await state.update_data(agency_id=agency_id)

    await state.set_state(CreateMaster.type)
    await choose_model_type(callback.message, state)
    await callback.answer()

@router.callback_query(F.data.startswith("create_model"))
async def start_create_master(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateMaster.type)
    await choose_model_type(callback.message, state)

    await callback.answer()

@router.callback_query(F.data.startswith("create_escort"))
async def start_create_master(callback: CallbackQuery, state: FSMContext):
    _, model_type = callback.data.split(":")
    await state.update_data(type=model_type)
    await state.set_state(CreateMaster.name)
    await callback.message.answer("Enter model's name:")
    await callback.answer()

# 3️⃣ Обработчики каждого поля
@router.message(CreateMaster.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateMaster.age)
    await message.answer("Enter age:")

@router.message(CreateMaster.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await state.set_state(CreateMaster.phonenumber)
    await message.answer("Enter phone number:")

@router.message(CreateMaster.phonenumber)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phonenumber=message.text)
    await state.set_state(CreateMaster.address)
    await message.answer("Enter address:")

@router.message(CreateMaster.address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(CreateMaster.height)
    await message.answer("Enter height (cm):")

@router.message(CreateMaster.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=float(message.text))
    await state.set_state(CreateMaster.weight)
    await message.answer("Enter weight (kg):")

@router.message(CreateMaster.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=float(message.text))
    await state.set_state(CreateMaster.cupsize)
    await message.answer("Enter cup size (number):")

@router.message(CreateMaster.cupsize)
async def process_cupsize(message: Message, state: FSMContext):
    await state.update_data(cupsize=int(message.text))
    await state.set_state(CreateMaster.clothsize)
    await message.answer("Enter cloth size:")

@router.message(CreateMaster.clothsize)
async def process_clothsize(message: Message, state: FSMContext):
    await state.update_data(clothsize=int(message.text))
    await state.set_state(CreateMaster.price_1h)
    await message.answer("Enter price for 1 hour:")

@router.message(CreateMaster.price_1h)
async def process_price_1h(message: Message, state: FSMContext):
    await state.update_data(price_1h=float(message.text))
    await state.set_state(CreateMaster.price_2h)
    await message.answer("Enter price for 2 hours:")

@router.message(CreateMaster.price_2h)
async def process_price_2h(message: Message, state: FSMContext):
    await state.update_data(price_2h=float(message.text))
    await state.set_state(CreateMaster.price_full_day)
    await message.answer("Enter price for full day:")

@router.message(CreateMaster.price_full_day)
async def process_price_day(message: Message, state: FSMContext):
    await state.update_data(price_full_day=float(message.text))
    await state.set_state(CreateMaster.photo)
    await message.answer("Now send the main photo of the model:")

# 4️⃣ Получение фото и сохранение модели
@router.message(CreateMaster.photo, F.content_type == "photo")
async def process_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photo = message.photo[-1]  # самый большой размер

    file = await bot.get_file(photo.file_id)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    await bot.download_file(file.file_path, destination=tmp.name)
    tmp.close()
    
    payload = {
        "name": data["name"],
        "age": str(data["age"]),
        "phonenumber": str(data["phonenumber"]),
        "address": data["address"],
        "height": str(data["height"]),
        "weight": str(data["weight"]),
        "cupsize": str(data["cupsize"]),
        "clothsize": str(data["clothsize"]),
        "price_1h": str(data["price_1h"]),
        "price_2h": str(data["price_2h"]),
        "price_full_day": str(data["price_full_day"]),
        "main_photo": "default.png",
        "is_top": str(data["type"] == "top")
    }
    
    url = f"{API_URL}/"

    if "agency_id" in data:
        url += f"agencies/{data['agency_id']}/masters/"
    else:
        url += f"masters/"

    with open(tmp.name, "rb") as f:
        files = {"file": f}
        resp = requests.post(url, data=payload, files=files, headers=headers)

    if resp.status_code in (200, 201):
        await message.answer("✅ Model created successfully!")
    else:
        await message.answer(f"❌ Error creating model: {resp.text}")

    os.remove(tmp.name)
    await state.clear()
