import logging
import requests
import json
from typing import Optional, Callable

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = 8275812174:AAHGIrL3Uw8AN7TKdNAtUZYFTi0lQu1Ni-A
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY_HERE"

def _default_get(url: str, **kwargs):
    return requests.get(url, **kwargs)

def get_weather(city: str, api_key: Optional[str] = None, requests_get: Callable = _default_get) -> Optional[str]:
    if not city:
        return None
    params = {
        "q": city,
        "units": "metric",
        "lang": "ru",
    }
    if api_key:
        params["appid"] = api_key
    url = "https://api.openweathermap.org/data/2.5/weather"
    r = requests_get(url, params=params)
    if not r or getattr(r, "status_code", None) != 200:
        return None
    try:
        data = r.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels = data['main']['feels_like']
        return f"Погода в {city} — {desc}, {temp}°C (ощущается как {feels}°C)"
    except Exception:
        return None

def get_forecast(city: str, api_key: Optional[str] = None, requests_get: Callable = _default_get) -> Optional[str]:
    if not city:
        return None
    params = {
        "q": city,
        "units": "metric",
        "lang": "ru",
    }
    if api_key:
        params["appid"] = api_key
    url = "https://api.openweathermap.org/data/2.5/forecast"
    r = requests_get(url, params=params)
    if not r or getattr(r, "status_code", None) != 200:
        return None
    try:
        data = r.json()
        parts = data.get("list", [])[:5]
        if not parts:
            return None
        result = [f"⏳ {item.get('dt_txt','?')}: {item['weather'][0]['description']}, {item['main']['temp']}°C" for item in parts]
        return "\n".join(result)
    except Exception:
        return None

# Try to import telegram only when needed. If it's missing, we still keep the core functions testable.
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except Exception:
    TELEGRAM_AVAILABLE = False

if TELEGRAM_AVAILABLE:
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Йоу! Напиши мне /w <город>, и я кину тебе прогноз.")

    async def forecast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Укажи город: /forecast Tokyo")
            return
        city = " ".join(context.args)
        info = get_forecast(city, api_key=OPENWEATHER_API_KEY)
        if info:
            await update.message.reply_text(f"Шаман Погоды 3000 предвидит:\n{info}")
        else:
            await update.message.reply_text("Не удалось заглянуть в будущее...")

    async def weather_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Укажи город: /w Berlin")
            return
        city = " ".join(context.args)
        info = get_weather(city, api_key=OPENWEATHER_API_KEY)
        if info:
            await update.message.reply_text(info)
        else:
            await update.message.reply_text("Не смог найти такой город...")

    def main_bot():
        if not TELEGRAM_TOKEN:
            logging.error("TELEGRAM_TOKEN is not set. Exiting.")
            return
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("w", weather_cmd))
        app.add_handler(CommandHandler("forecast", forecast_cmd))
        app.run_polling()

else:
    def main_bot():
        logging.warning("python-telegram-bot not available in this environment. Bot functionality disabled.")

if __name__ == "__main__":
    # Simple CLI fallback so the module can still be used without telegram installed.
    import sys
    if len(sys.argv) >= 3 and sys.argv[1] == "weather":
        city = " ".join(sys.argv[2:])
        print(get_weather(city, api_key=None))
    elif len(sys.argv) >= 3 and sys.argv[1] == "forecast":
        city = " ".join(sys.argv[2:])
        print(get_forecast(city, api_key=None))
    else:
        print("telegram not available; running tests instead. Use: python file.py weather <city> or forecast <city>")

# Unit tests
import unittest
from unittest.mock import Mock

class TestWeatherParsing(unittest.TestCase):
    def test_get_weather_success(self):
        sample = {
            'weather': [{'description': 'ясно'}],
            'main': {'temp': 10, 'feels_like': 8}
        }
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample
        def fake_get(url, params=None):
            return mock_resp
        res = get_weather("Moscow", api_key=None, requests_get=fake_get)
        self.assertIn("Погода в Moscow", res)
        self.assertIn("ясно", res)

    def test_get_weather_http_error(self):
        mock_resp = Mock()
        mock_resp.status_code = 404
        mock_resp.json.return_value = {}
        def fake_get(url, params=None):
            return mock_resp
        res = get_weather("NoCity", api_key=None, requests_get=fake_get)
        self.assertIsNone(res)

    def test_get_forecast_success(self):
        sample = {
            'list': [
                {'dt_txt': '2025-12-12 12:00:00', 'weather': [{'description': 'облачно'}], 'main': {'temp': 5}},
                {'dt_txt': '2025-12-12 15:00:00', 'weather': [{'description': 'дождь'}], 'main': {'temp': 4}},
            ]
        }
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample
        def fake_get(url, params=None):
            return mock_resp
        res = get_forecast("Berlin", api_key=None, requests_get=fake_get)
        self.assertIn("⏳ 2025-12-12 12:00:00", res)
        self.assertIn("облачно", res)

    def test_get_forecast_no_list(self):
        sample = {'list': []}
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = sample
        def fake_get(url, params=None):
            return mock_resp
        res = get_forecast("EmptyTown", api_key=None, requests_get=fake_get)
        self.assertIsNone(res)

if __name__ == '__main__':
    unittest.main()
