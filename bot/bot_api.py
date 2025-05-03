from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

app = FastAPI()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

class AppointmentNotification(BaseModel):
    user_id: int
    doctor: str
    hospital: str
    datetime: str  # ISO формат

@app.post("/notify")
async def notify_appointment(data: AppointmentNotification):
    try:
        message = (
            f"✅ Вы записаны!\n"
            f"🏥 Больница: {data.hospital}\n"
            f"👨‍⚕️ Врач: {data.doctor}\n"
            f"📅 Дата и время: {data.datetime}"
        )
        await bot.send_message(chat_id=data.user_id, text=message)
        logging.info(f"Сообщение отправлено пользователю {data.user_id}")
        return {"status": "OK"}
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))