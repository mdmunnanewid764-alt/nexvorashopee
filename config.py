import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8864898167:AAH5cSW1zJEUC6MXP3c6rz7DQY1WsMDgj3U")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6575066703"))
BINANCE_API_BASE_URL = os.getenv("BINANCE_API_BASE_URL", "https://binance-api-yrz4.onrender.com").rstrip("/")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "bg_live_your_merchant_api_key")
CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "$")
CURRENCY_NAME = os.getenv("CURRENCY_NAME", "USDT")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@Support")
DATABASE_PATH = os.getenv("DATABASE_PATH", "nexvora_shop.db")
MIN_DEPOSIT = float(os.getenv("MIN_DEPOSIT", "1.0"))
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL", "").strip() or None
TELEGRAM_BASE_URL = os.getenv("TELEGRAM_BASE_URL", "").strip() or None
ORDER_LOG_GROUP_ID = os.getenv("ORDER_LOG_GROUP_ID", "-1003721268860")
