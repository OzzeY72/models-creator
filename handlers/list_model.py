from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, tempfile
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import os
import tempfile
from utils import format_master, preload_image

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")

router = Router()
models_cache = []

def get_master_keyboard(current: int, total: int, master_id: str) -> InlineKeyboardMarkup:
  return InlineKeyboardMarkup(
    inline_keyboard=[
      [
        InlineKeyboardButton(text="⬅️", callback_data=f"prev_models:{current}"),
        InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="noop"),
        InlineKeyboardButton(text="➡️", callback_data=f"next_models:{current}")
      ],
      [
          InlineKeyboardButton(text="Menu", callback_data="go_home")
      ]
    ]
  )

def get_main_menu():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="Top Escort", callback_data="show_models:top"),
              InlineKeyboardButton(text="Escort", callback_data="show_models:regular"),
          ],
          [
              InlineKeyboardButton(text="Agencies", callback_data="show_agencyspa:agencies"),
              InlineKeyboardButton(text="SPA", callback_data="show_agencyspa:spa"),
          ]
      ]
  )

async def list_models_block(message: Message):
  text = (
      "TEMPLATE\n"
      "Welcome to Admin bot\n\n"
  )

  await message.answer(text=text, reply_markup=get_main_menu())

@router.callback_query(F.data.startswith("go_home"))
async def go_home(callback: CallbackQuery):
  await list_models_block(callback.message)
  await callback.answer()

@router.message(lambda m: m.text == "📋 List")
async def list_models(message: Message):
   await list_models_block(message)

@router.callback_query(F.data.startswith("show_models"))
async def list_models(callback: CallbackQuery):
    print("SHOW MODELS")
    _, category = callback.data.split(":")
    url = f"{API_URL}/{'top' if category == 'top' else 'regular'}/"

    resp = requests.get(url)
    resp.raise_for_status()
    global models_cache
    models_cache = resp.json()

    if not models_cache:
        await callback.message.answer("📭 No models found")
        await callback.answer()
        return

    current = 0
    m = models_cache[current]

    text = format_master(m)
    kb = get_master_keyboard(current, len(models_cache), m.get("id"))

    if m.get("main_photo"):
        photo = await preload_image(m, API_URL)
        await callback.message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await callback.message.answer(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("prev_models"))
async def prev_master(callback: CallbackQuery):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current - 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_master_keyboard(new_index, total, m.get("id"))

    await update_master_message(callback, m, text, kb, new_index)

# Перелистывание вперёд
@router.callback_query(F.data.startswith("next_models"))
async def next_master(callback: CallbackQuery):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current + 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_master_keyboard(new_index, total, m.get("id"))

    await update_master_message(callback, m, text, kb, new_index)

async def update_master_message(callback: CallbackQuery, m, text, kb, new_index):
    if m.get("main_photo"):
      photo = await preload_image(m, API_URL)
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
