import os
import asyncio
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher,F
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
import redis.asyncio as aioredis
import json 

from handlers.create_model import router as create_master_router
from handlers.list_model import router as list_masters_router
from handlers.start import router as start_router
from handlers.edit_model import router as edit_router
from handlers.application import router as application_router
from handlers.list_agencies import router as agencies_router
from handlers.create_agency import router as agencies_create_router

from aiogram.fsm.storage.memory import MemoryStorage

# Загружаем .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

redis = aioredis.from_url(REDIS_URL, decode_responses=True)

async def redis_listener(bot: Bot):
    pubsub = redis.pubsub()
    await pubsub.subscribe("applications_channel")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            text = f"📩 New application ({data['total']})"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📜 Show applications", callback_data=f"show_apps")]
            ])
            await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, reply_markup=kb)

async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start_router)
    dp.include_router(create_master_router)
    dp.include_router(list_masters_router)
    dp.include_router(edit_router)
    dp.include_router(application_router)
    dp.include_router(agencies_router)
    dp.include_router(agencies_create_router)

    # запускаем слушатель в фоне
    asyncio.create_task(redis_listener(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

# # Настраиваем бота
# bot = Bot(
#     token=BOT_TOKEN,
#     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
# )
# dp = Dispatcher(storage=MemoryStorage())
# dp.include_router(start_router)
# dp.include_router(create_master_router)
# dp.include_router(list_masters_router)
# dp.include_router(edit_router)

# if __name__ == "__main__":
#   asyncio.create_task(redis_listener(bot))
#   asyncio.run(dp.start_polling(bot))
