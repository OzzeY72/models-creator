from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import requests
from states import EditMaster
import os
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram import Bot, F
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import tempfile
from utils import format_master, preload_image

load_dotenv()
router = Router()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

def get_edit_keyboard(master_id: int) -> InlineKeyboardMarkup:
    buttons = [
      ("Name", "name"), ("Age", "age"), ("Phone", "phonenumber"),
      ("Address", "address"), ("Height", "height"), ("Weight", "weight"),
      ("Cup", "cupsize"), ("Cloth size", "clothsize"),
      ("Price 1h", "price_1h"), ("Price 2h", "price_2h"),
      ("Full day", "price_full_day"), ("Photo", "main_photo")
    ]

    inline_keyboard = []
    row = []
    for i, (label, field) in enumerate(buttons, start=1):
      row.append(InlineKeyboardButton(text=label, callback_data=f"edit_post:{master_id}:{field}"))
      if i % 2 == 0:
        inline_keyboard.append(row)
        row = []
    if row:
      inline_keyboard.append(row) 

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

async def show_edit_master(target, master_id: int, state: FSMContext):
    resp = requests.get(f"{API_URL}/masters/{master_id}")
    if resp.status_code != 200:
      await target.answer("❌ Could not fetch model")
      return

    m = resp.json()
    await state.update_data(master_id=master_id, m=m)
    text = format_master(m)
    kb = get_edit_keyboard(master_id)

    await state.set_state(EditMaster.field)

    if m.get("main_photo"):
      photo = await preload_image(m, API_URL)
      await target.answer_photo(photo, caption=text, reply_markup=kb)
    else:
      await target.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("edit:"))
async def edit_master(callback: CallbackQuery, state: FSMContext):
  _, master_id = callback.data.split(":")
  await show_edit_master(callback.message, master_id, state)
  await callback.answer()

@router.callback_query(F.data.startswith("edit_post"))
async def edit_master_callback(callback: CallbackQuery, state: FSMContext):
  _, master_id, field = callback.data.split(":")
  await state.update_data(field=field)

  if field == "photo":
    await state.set_state(EditMaster.value)
    await callback.message.answer("Send new photo:")
  else:
    await state.set_state(EditMaster.value)
    await callback.message.answer(f"Enter new value for {field}:")
  
  await callback.answer()

@router.message(EditMaster.value)
async def process_edit_value(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    print(data)
    master_id = data["master_id"]
    field = data["field"]
    m = data["m"]

    if field == "main_photo":
      photo = message.photo[-1]
      file = await bot.get_file(photo.file_id)
      tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
      await bot.download_file(file.file_path, destination=tmp.name)
      tmp.close()
      with open(tmp.name, "rb") as f:
        m["main_photo"] = f"{master_id}.jpg"
        files = {"file": f}
        resp = requests.post(f"{API_URL}/masters/{master_id}/upload_photo", files=files, headers=headers)
        if resp.status_code == 200:
          print("✅ Model created successfully!")
        else:
          print(f"❌ Error uploading photo: {resp.text}")
    else:
      m[field] = message.text
      resp = requests.put(f"{API_URL}/masters/{master_id}", json=m, headers=headers)

    if resp.status_code in (200, 201):
      await state.set_state(EditMaster.view)
      await show_edit_master(message, master_id, state)
      # await message.answer("✅ Updated successfully!")
    else:
        await message.answer(f"❌ Update failed: {resp.text}")

    # await state.clear()
