import requests, tempfile
from aiogram.types import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL")

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

def format_agencyspa(a: dict) -> str:
  return (
    f"🏢 <b>{a.get('name')}</b>\n"
    f"📍 Address: {a.get('address', 'N/A')}\n"
    f"📞 Phone: {a.get('phone', 'N/A')}\n"
  )

def format_application(app: dict) -> str:
    if "age" in app:  # значит это модель
        return format_master(app)
    else:  # значит spa/agency
        return format_agencyspa(app)

def get_agency_keyboard(current: int, total: int, agency_id: str) -> InlineKeyboardMarkup:
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(text="⬅️", callback_data=f"agency_prev:{current}"),
              InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="noop"),
              InlineKeyboardButton(text="➡️", callback_data=f"agency_next:{current}")
          ],
          [
              InlineKeyboardButton(text="Choose this", callback_data=f"agency_choose:{agency_id}"),
          ],
          [
              InlineKeyboardButton(text="🏠 Menu", callback_data="go_home")
          ]
      ]
  )

async def send_master_carousel(message, masters, state, index=0):
    m = masters[index]
    text = format_master(m)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"prev:{index}"),
            InlineKeyboardButton(text=f"{index+1}/{len(masters)}", callback_data="noop"),
            InlineKeyboardButton(text="➡️", callback_data=f"next:{index}")
        ],
        [
            InlineKeyboardButton(text="Menu", callback_data="go_home")
        ]
    ])

    if m.get("main_photo"):
        photo = await preload_image(m, API_URL)
        await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

async def send_agencies_carousel(message, agency_spa, state: FSMContext, total: int, index=0):
    if not agency_spa:
      await message.answer("🚫 No Agencies / SPA")
      return
    
    agency = agency_spa[index]
    text = format_application(agency)

    kb = get_agency_keyboard(index, total, agency.get("id"))

    if agency.get("photos") and len(agency["photos"]) > 0:
       photo_url = agency["photos"][0] 
       photo = await preload_image({"main_photo": photo_url}, API_URL)
       await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

def get_application_keyboard(current: int, total: int, agency_id: str) -> InlineKeyboardMarkup:
  return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️", callback_data=f"app_prev:{current}"),
                InlineKeyboardButton(text=f"{current+1}/{total}", callback_data="noop"),
                InlineKeyboardButton(text="➡️", callback_data=f"app_next:{current}")
            ],
            [
                InlineKeyboardButton(text="✅ Approve", callback_data=f"app_approve:{agency_id}"),
                InlineKeyboardButton(text="❌ Decline", callback_data=f"app_decline:{agency_id}")
            ],
            [
                InlineKeyboardButton(text="🏠 Menu", callback_data="go_home")
            ]
        ]
    ) 

async def send_applications_carousel(message, applications, state: FSMContext, index=0):
    if not applications:
        await message.answer("🚫 No applications")
        return
    
    app = applications[index]
    text = format_application(app)

    kb = get_application_keyboard(index, len(applications), app.get("id"))

    if app.get("main_photo"): 
        photo = await preload_image(app, API_URL)
        await message.answer_photo(photo, caption=text, reply_markup=kb)
    elif app.get("photos") and len(app["photos"]) > 0:
       photo_url = app["photos"][0] 
       photo = await preload_image({"main_photo": photo_url}, API_URL)
       await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)

async def preload_image(m, API_URL) :
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