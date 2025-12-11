import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY"

logging.basicConfig(level=logging.INFO)

def get_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    desc = data['weather'][0]['description']
    temp = data['main']['temp']
    feels = data['main']['feels_like']
    return f"Погода в {city} — {desc}, {temp}°C (ощущается как {feels}°C)"

def get_forecast(city: str):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    parts = data["list"][:5]
    result = [f"⏳ {item['dt_txt']}: {item['weather'][0]['description']}, {item['main']['temp']}°C" for item in parts]
    return "\n".join(result)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Йоу! Напиши мне /w <город>, и я кину тебе прогноз.")

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи город: /forecast Tokyo")
        return
    city = " ".join(context.args)
    info = get_forecast(city)
    if info:
        await update.message.reply_text(f"Шаман Погоды 3000 предвидит:\n{info}")
    else:
        await update.message.reply_text("Не удалось заглянуть в будущее...")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Укажи город: /w Berlin")
        return
    city = " ".join(context.args)
    info = get_weather(city)
    if info:
        await update.message.reply_text(info)
    else:
        await update.message.reply_text("Не смог найти такой город...")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("w", weather))
    app.add_handler(CommandHandler("forecast", forecast))
    app.run_polling()

if __name__ == "__main__":
    main()
