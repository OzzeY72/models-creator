from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import requests
from states import CreateAgencySpa, CreateMaster
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
import os
from aiogram import Bot, F
from dotenv import load_dotenv
import tempfile

load_dotenv()
router = Router()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

router = Router()

async def work_with_us(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏢 Agency", callback_data="apply_agency")],
        [InlineKeyboardButton(text="🏖️ SPA", callback_data="apply_spa")],
    ])
    await message.answer("Choose agency or spa:", reply_markup=kb)

@router.message(F.text == "🏢 Add agency / spa")
async def start_create_agency(message: Message, state: FSMContext):
    await work_with_us(message, state)

@router.callback_query(F.data == "apply_agency")
async def apply_agency(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAgencySpa.name)
    await callback.message.answer("Enter agency name:")
    await state.update_data(is_agency=True)
    await callback.answer()

@router.callback_query(F.data == "apply_spa")
async def apply_spa(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CreateAgencySpa.name)
    await callback.message.answer("Enter SPA name:")
    await state.update_data(is_agency=False)
    await callback.answer()

@router.message(CreateAgencySpa.name)
async def process_agency_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CreateAgencySpa.phone)
    await message.answer("Enter phone:")

@router.message(CreateAgencySpa.phone)
async def process_agency_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CreateAgencySpa.address)
    await message.answer("Enter address:")

@router.message(CreateAgencySpa.address)
async def process_agency_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(CreateAgencySpa.photos)
    await message.answer("Now send photo:")

@router.message(CreateAgencySpa.photos, F.content_type == "photo")
async def process_agency_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photo = message.photo[-1]

    # получаем файл с Telegram
    file = await bot.get_file(photo.file_id)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    await bot.download_file(file.file_path, destination=tmp.name)
    tmp.close()

    # собираем payload и files для form-data
    payload = {
        "name": data["name"],
        "phone": data["phone"],
        "is_agency": data["is_agency"],
        "address": data.get("address", ""),
    }

    with open(tmp.name, "rb") as f:
        files = {"files": [f]}
        resp = requests.post(f"{API_URL}/agencies/", data=payload, files=files, headers=headers)

    if resp.status_code in (200, 201):
        await message.answer("✅ Agency / SPA created successfully!")
    else:
        await message.answer(f"❌ Error created Agency / SPA: {resp.text}")

    os.remove(tmp.name)
    await state.clear()