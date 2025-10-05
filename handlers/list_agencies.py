from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests, tempfile
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
import os
import tempfile
from utils import format_agencyspa, format_master, get_masters_keyboard, preload_image, send_master_carousel

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
API_URL_HTTPS = os.getenv("API_URL_HTTPS")

router = Router()
models_cache = []

def get_agencyspa_keyboard(current: int, total: int, agency_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📷 Show Photos",
                web_app=WebAppInfo(url=f"{API_URL_HTTPS}/agencies_view/{agency_id}")
            )],
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"prev_agency:{current}"),
                InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="noop"),
                InlineKeyboardButton(text="➡️", callback_data=f"next_agency:{current}"),
            ],
            [InlineKeyboardButton(text="Open", callback_data=f"open_spa:{agency_id}")]
        ]
    )

@router.callback_query(F.data.startswith("open_spa"))
async def open_spa_agency(callback: CallbackQuery, state: FSMContext):
    _, spa_id = callback.data.split(":")
    
    # Получаем модели SPA/Agency
    resp = requests.get(f"{API_URL}/masters/by_spa/{spa_id}/",)
    if resp.status_code != 200:
        await callback.answer("❌ Could not fetch models", show_alert=True)
        return

    masters = resp.json()
    global models_cache
    models_cache = masters

    if not masters:
        await callback.answer("📭 No models found", show_alert=True)
        return

    # Сохраняем в state
    await state.update_data(search_results=masters)
    await send_master_carousel(callback.message, masters, state, index=0, prev_name="prev_opened", next_name="next_opened")
    await callback.answer()

async def update_master_message(callback: CallbackQuery, m, text, kb, new_index):
    if m.get("photos"):
      photo = await preload_image(m, API_URL)
      media = InputMediaPhoto(media=photo, caption=text)
      await callback.message.edit_media(media=media, reply_markup=kb)
    else:
      try:
        await callback.message.edit_caption(caption=text, reply_markup=kb)
      except:
        await callback.message.edit_text(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("prev_opened"))
async def prev(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current - 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_masters_keyboard(new_index, total, m.get("id"), prev_name="prev_opened", next_name="next_opened")

    await update_master_message(callback, m, text, kb, new_index)

@router.callback_query(F.data.startswith("next_opened"))
async def next(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(models_cache)

    new_index = (current + 1) % total
    m = models_cache[new_index]
    text = format_master(m)
    kb = get_masters_keyboard(new_index, total, m.get("id"), prev_name="prev_opened", next_name="next_opened")

    await update_master_message(callback, m, text, kb, new_index)

@router.callback_query(F.data.startswith("show_agencyspa"))
async def list_agencyspa(callback: CallbackQuery):
    print("SHOW AGENCY")
    _, category = callback.data.split(":")
    url = f"{API_URL}/agencies/{category}/"

    resp = requests.get(url)
    resp.raise_for_status()
    global agencies_cache
    agencies_cache = resp.json()

    if not agencies_cache:
        await callback.message.answer("📭 No agencies or SPA found", show_alert=True)
        await callback.answer()
        return

    current = 0
    a = agencies_cache[current]

    text = format_agencyspa(a)
    kb = get_agencyspa_keyboard(current, len(agencies_cache), a.get("id"))

    if a.get("photos"):
        photo = await preload_image(a, API_URL)
        await callback.message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await callback.message.answer(text, reply_markup=kb)

    await callback.answer()

@router.callback_query(F.data.startswith("prev_agency"))
async def prev_agency(callback: CallbackQuery):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(agencies_cache)

    new_index = (current - 1) % total
    a = agencies_cache[new_index]
    text = format_agencyspa(a)
    kb = get_agencyspa_keyboard(new_index, total, a.get("id"))

    await update_agencyspa_message(callback, a, text, kb)

@router.callback_query(F.data.startswith("next_agency"))
async def next_agency(callback: CallbackQuery):
    print("NEXT AGENCY")
    _, current = callback.data.split(":")
    current = int(current)
    total = len(agencies_cache)

    new_index = (current + 1) % total
    a = agencies_cache[new_index]
    text = format_agencyspa(a)
    kb = get_agencyspa_keyboard(new_index, total, a.get("id"))

    await update_agencyspa_message(callback, a, text, kb)


async def update_agencyspa_message(callback: CallbackQuery, a, text, kb):
    if a.get("photos"):
        photo = await preload_image(a, API_URL)
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
