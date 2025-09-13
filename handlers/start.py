from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

import tempfile

router = Router()

# --- Main menu ---
menu = ReplyKeyboardMarkup(
  keyboard=[
    [KeyboardButton(text="➕ Add model")],
    [KeyboardButton(text="📋 List models")],
  ],
  resize_keyboard=True
)

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello 👋 I am bot to manage models!", reply_markup=menu)