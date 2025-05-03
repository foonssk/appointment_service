import os
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')  # Название переменной из .env
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')  # Название переменной из .env
        self.bot = Bot(token=self.token) if self.token else None
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    async def send_notification(self, message: str):
        if not self.bot:
            logger.warning("Telegram bot token not configured. Notification not sent.")
            return
            
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            logger.info("Telegram notification sent successfully.")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    def schedule_reminder(self, appointment_info: dict):
        if not self.bot:
            return
            
        # Парсим дату приёма
        appointment_date = datetime.strptime(appointment_info['appointment_date'], "%Y-%m-%d %H:%M:%S")
        
        # Отправляем уведомление о записи сразу
        immediate_message = (
            f"✅ Вы успешно записаны на приём!\n"
            f"🏥 Больница: {appointment_info['hospital_name']}\n"
            f"👨‍⚕️ Врач: {appointment_info['doctor_name']}\n"
            f"📅 Дата: {appointment_date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {appointment_date.strftime('%H:%M')}"
        )
        self.scheduler.add_job(
            self.send_notification,
            'date',
            run_date=datetime.now(),
            args=[immediate_message]
        )
        
        # Напоминание за день до приёма
        reminder_date = appointment_date - timedelta(days=1)
        if reminder_date > datetime.now():
            reminder_message = (
                f"🔔 Напоминание о записи на завтра!\n"
                f"🏥 Больница: {appointment_info['hospital_name']}\n"
                f"👨‍⚕️ Врач: {appointment_info['doctor_name']}\n"
                f"📅 Дата: {appointment_date.strftime('%d.%m.%Y')}\n"
                f"⏰ Время: {appointment_date.strftime('%H:%M')}"
            )
            self.scheduler.add_job(
                self.send_notification,
                'date',
                run_date=reminder_date,
                args=[reminder_message]
            )
    
    def start(self):
        if self.bot:
            self.scheduler.start()

# Глобальный экземпляр для использования в других модулях
telegram_notifier = TelegramNotifier()