from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import requests
from states import CreateMaster
import os
from aiogram import Bot, F
from dotenv import load_dotenv
import tempfile

load_dotenv()
router = Router()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

# 2️⃣ Старт процесса
@router.message(F.text == "➕ Add model")
async def start_create_master(message: Message, state: FSMContext):
    await state.set_state(CreateMaster.name)
    await message.answer("Enter model's name:")

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

    # создаём модель на бекенде без фото
    payload = {
        "name": data["name"],
        "age": data["age"],
        "phonenumber": data["phonenumber"],
        "address": data["address"],
        "height": data["height"],
        "weight": data["weight"],
        "cupsize": data["cupsize"],
        "clothsize": data["clothsize"],
        "price_1h": data["price_1h"],
        "price_2h": data["price_2h"],
        "price_full_day": data["price_full_day"],
        "main_photo": "default.png"
    }
    resp = requests.post(f"{API_URL}/masters/", json=payload, headers=headers)
    if resp.status_code > 299:
        print(resp.status_code)
        await message.answer(f"❌ Error creating model: {resp.text}")
        await state.clear()
        return

    model_id = resp.json()["id"]

    file = await bot.get_file(photo.file_id)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    await bot.download_file(file.file_path, destination=tmp.name)
    tmp.close()
    with open(tmp.name, "rb") as f:
      files = {"file": f}
      resp2 = requests.post(f"{API_URL}/masters/{model_id}/upload_photo", files=files, headers=headers)

    if resp2.status_code == 200:
        await message.answer("✅ Model created successfully!")
    else:
        await message.answer(f"❌ Error uploading photo: {resp2.text}")

    await state.clear()
