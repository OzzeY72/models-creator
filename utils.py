import requests, tempfile
from aiogram.types import FSInputFile

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