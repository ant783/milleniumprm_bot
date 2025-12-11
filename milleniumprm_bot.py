from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import random

# Команда старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-повторяшка с юмором. Напиши что-нибудь, и я повторю с шуткой!")

# Список шуток
jokes = [
    "😂 Это звучит знакомо!",
    "😎 Я бы сам так сказал!",
    "🤣 Хаха, прикольно!",
    "😏 Неожиданно, но верно!",
    "😜 Согласен на все 100!"
]

# Повторение сообщений с шуткой
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    joke = random.choice(jokes)
    await update.message.reply_text(f"{text}\n{joke}")

if __name__ == '__main__':
    # Создаём приложение с токеном
    app = ApplicationBuilder().token("8275812174:AAHGIrL3Uw8AN7TKdNAtUZYFTi0lQu1Ni-A").build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запуск
    app.run_polling()
