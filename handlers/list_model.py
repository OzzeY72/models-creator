from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, tempfile
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os
import tempfile

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

router = Router()
headers = {"X-API-Key": API_KEY}

models_cache = []

def get_master_keyboard(current: int, total: int) -> InlineKeyboardMarkup:
  return InlineKeyboardMarkup(
    inline_keyboard=[
      [
        InlineKeyboardButton(text="⬅️", callback_data=f"prev:{current}"),
        InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="noop"),
        InlineKeyboardButton(text="➡️", callback_data=f"next:{current}")
      ]
    ]
  )

def format_master(m: dict) -> str:
    return (
      f"👩 <b>{m['name']}</b>, {m['age']} y.o.\n\n"
      f"📞 Phone: {m['phonenumber']}\n"
      f"🏠 Address: {m['address']}\n\n"
      f"📐 Parameters:\n"
      f"   Height: {m['height']} cm | Weight: {m['weight']} kg\n"
      f"   Cup: {m['cupsize']} | Cloth size: {m['clothsize']}\n\n"
      f"💰 Prices:\n"
      f"   1 hour: {m['price_1h']} $\n"
      f"   2 hours: {m['price_2h']} $\n"
      f"   Full day: {m['price_full_day']} $\n\n"
      f"📲 Call: {m['phonenumber']}"
    )

async def preload_image(m) :
    if m.get("main_photo"):
      try:
        photo_resp = requests.get(f"{API_URL}/static/{m['main_photo']}", stream=True)
        photo_resp.raise_for_status()

        if "image" not in photo_resp.headers.get("content-type", ""):
          print(f"⚠️ Not an image URL")

        # временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
          for chunk in photo_resp.iter_content(1024):
            tmp.write(chunk)
          tmp_path = tmp.name

        photo = FSInputFile(tmp_path)
        return photo

      except Exception as e:
        print(f"⚠️ Could not load photo: {e}")

@router.message(lambda m: m.text == "📋 List models")
async def list_models(message: Message):
    resp = requests.get(f"{API_URL}/masters/", headers=headers)
    resp.raise_for_status()
    global models_cache
    models_cache = resp.json()

    if not models_cache:
        await message.answer("📭 No models found")
        return

    current = 0
    text = format_master(models_cache[current])
    kb = get_master_keyboard(current, len(models_cache))

    m = models_cache[current]

    if m.get("main_photo"):
      photo = await preload_image(m)
      await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
      await message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("prev"))
async def prev_master(callback: CallbackQuery):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current - 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_master_keyboard(new_index, total)

    await update_master_message(callback, m, text, kb, new_index)

# Перелистывание вперёд
@router.callback_query(F.data.startswith("next"))
async def next_master(callback: CallbackQuery):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current + 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_master_keyboard(new_index, total)

    await update_master_message(callback, m, text, kb, new_index)

async def update_master_message(callback: CallbackQuery, m, text, kb, new_index):
    if m.get("main_photo"):
      photo = await preload_image(m)
      media = InputMediaPhoto(media=photo, caption=text)
      await callback.message.edit_media(media=media, reply_markup=kb)
    else:
      try:
        await callback.message.edit_caption(caption=text, reply_markup=kb)
      except:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()
