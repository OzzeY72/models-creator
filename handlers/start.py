from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.types import CallbackQuery

import tempfile

router = Router()

# --- Main menu ---
menu = ReplyKeyboardMarkup(
  keyboard=[
    [KeyboardButton(text="📋 List")],
    [KeyboardButton(text="➕ Add model")],
    [KeyboardButton(text="🏢 Add agency / spa")],
  ],
  resize_keyboard=True
)

@router.message(Command("start"))
async def start(message: Message):
    print(message.chat.id)
    await message.answer("Hello 👋 I am bot to manage models!", reply_markup=menu)