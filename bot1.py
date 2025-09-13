import os
import asyncio
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher,F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from handlers.create_model import router as create_master_router
from handlers.list_model import router as list_masters_router
from handlers.start import router as start_router

from aiogram.fsm.storage.memory import MemoryStorage

# Загружаем .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настраиваем бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(start_router)
dp.include_router(create_master_router)
dp.include_router(list_masters_router)

if __name__ == "__main__":
  asyncio.run(dp.start_polling(bot))
