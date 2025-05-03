import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from bot.config import TELEGRAM_BOT_TOKEN, FASTAPI_URL
import httpx

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Привет, {update.effective_user.first_name}!\nЯ ваш помощник.')

# Команда /hello
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FASTAPI_URL}/hello")
        data = response.json()
        await update.message.reply_text(data['message'])

# Основная функция запуска бота
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hello", hello))

    print("Telegram-бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()