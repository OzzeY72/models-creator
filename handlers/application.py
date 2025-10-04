from email.mime import application
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
import requests
from states import CreateMaster
import os
from aiogram import Bot, F
from dotenv import load_dotenv
import tempfile

from utils import format_application, get_application_keyboard, preload_image, send_applications_carousel

load_dotenv()
router = Router()

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
headers = {"X-API-Key": API_KEY}

applications_cache = []

async def get_apps(callback: CallbackQuery, state: FSMContext):
    resp = requests.get(f"{API_URL}/applications")
    if resp.status_code != 200:
        await callback.answer("❌ Error while fetching applications")
        return

    applications = resp.json()
    
    if not applications:
        await callback.message.answer("📭 No pending applications")
        return
    
    all_apps = applications["models"] + applications["agencies_spa"]
    global applications_cache
    applications_cache = all_apps
    await state.update_data(applications=all_apps)

@router.callback_query(F.data == "show_apps")
async def show_apps(callback: CallbackQuery, state: FSMContext):
    await get_apps(callback, state)
    apps = await state.get_data()
    await send_applications_carousel(callback.message, apps["applications"], state, index=0)

async def update_application_message(callback: CallbackQuery, app, text, kb, new_index):
    if app.get("photos"): 
        photo = await preload_image(app, API_URL)
        media = InputMediaPhoto(media=photo, caption=text)
        await callback.message.edit_media(media=media, reply_markup=kb)
    else:
        await callback.message.edit_caption(text, reply_markup=kb)

@router.callback_query(F.data.startswith("app_prev"))
async def app_prev(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(applications_cache)

    new_index = (current - 1) % total
    app = applications_cache[new_index]
    text = format_application(app)
    kb = get_application_keyboard(new_index, total, app.get("id"))

    await update_application_message(callback, app=app, text=text, kb=kb, new_index=new_index)
    await callback.answer()


@router.callback_query(F.data.startswith("app_next"))
async def app_next(callback: CallbackQuery, state: FSMContext):
    _, current = callback.data.split(":")
    current = int(current)
    total = len(applications_cache)

    new_index = (current + 1) % total
    print(new_index)
    app = applications_cache[new_index]
    text = format_application(app)
    kb = get_application_keyboard(new_index, total, app.get("id"))

    await update_application_message(callback, app=app, text=text, kb=kb, new_index=new_index)
    await callback.answer()

@router.callback_query(F.data.startswith("app_decline"))
async def app_decline(callback: CallbackQuery, state: FSMContext):
    _, id = callback.data.split(":")

    resp = requests.post(f"{API_URL}/applications/{id}/decline", headers=headers)

    message = ""
    if resp.status_code == 200:
        message = "✅ Application deleted successfully!"
        await get_apps(callback, state)
    else:
        message = f"❌ Error deleting application: {resp.text}"
    
    print(message)
    await callback.answer(message, show_alert=True)

@router.callback_query(F.data.startswith("app_approve"))
async def app_approve(callback: CallbackQuery, state: FSMContext):
    _, id = callback.data.split(":")

    resp = requests.post(f"{API_URL}/applications/{id}/approve", headers=headers)
    message = ""
    if resp.status_code == 200:
        message = "✅ Application approved successfully!"
        await get_apps(callback, state)
    else:
        message = f"❌ Error approved application: {resp.text}"

    print(message)
    await callback.answer(message, show_alert=True)
