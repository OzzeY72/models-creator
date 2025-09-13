from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

import tempfile

router = Router()

# --- Главное меню ---
menu = ReplyKeyboardMarkup(
  keyboard=[
    [KeyboardButton(text="➕ Add model")],
    [KeyboardButton(text="📋 List models")],
    [KeyboardButton(text="✏️ Change model")]
  ],
  resize_keyboard=True
)

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет 👋 Я бот для управления моделями!", reply_markup=menu)