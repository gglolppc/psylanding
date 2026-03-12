import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()

async def send_booking_notification(booking):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    text = (
        f"🚀 Новая заявка!\n\n"
        f"👤 Имя: {booking.name}\n"
        f"📞 Тел: {booking.phone}\n"
        f"📧 Email: {booking.email}\n"
        f"⏰ Время: {booking.preferred_time}\n"
        f"💬 Сообщение: {booking.message}"
    )

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json={"chat_id": chat_id, "text": text})
            if res.status_code != 200:
                print(f"Ошибка ТГ: {res.text}")
        except Exception as e:
            print(f"Ошибка запроса: {e}")