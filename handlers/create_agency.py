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

def send_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Send", callback_data="send_agency_form")]
    ])

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
    await state.set_state(CreateAgencySpa.model_count)
    await message.answer("Enter model count for this agency:")

@router.message(CreateAgencySpa.model_count)
async def process_agency_model_count(message: Message, state: FSMContext):
    await state.update_data(model_count=int(message.text))
    await state.set_state(CreateAgencySpa.photos)
    await message.answer(
        "Now send photos one by one.\nWhen done, click 📤 Send below.",
        reply_markup=send_button()
    )

@router.message(CreateAgencySpa.photos, F.content_type == "photo")
async def collect_photos(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    photos = data.get("photos", [])

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    await bot.download_file(file.file_path, destination=tmp.name)
    tmp.close()

    photos.append(tmp.name)
    await state.update_data(photos=photos)

@router.callback_query(F.data == "send_agency_form")
async def send_agency_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if not photos:
        await callback.message.answer("⚠️ You need to send at least one photo!")
        await callback.answer()
        return

    payload = {
        "name": data["name"],
        "phone": data["phone"],
        "is_agency": data["is_agency"],
        "address": data.get("address", ""),
        "model_count": data.get("model_count", 5),
    }

    files = [("files", (os.path.basename(p), open(p, "rb"), "image/jpeg")) for p in photos]

    try:
        resp = requests.post(f"{API_URL}/agencies/", data=payload, files=files, headers=headers)

        if resp.status_code in (200, 201):
            await callback.message.answer("✅ Agency / SPA created successfully!")
        else:
            await callback.message.answer(f"❌ Error creating: {resp.text}")
    finally:
        for p in photos:
            os.remove(p)

    await state.clear()
    await callback.answer()