import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8864898167:AAH5cSW1zJEUC6MXP3c6rz7DQY1WsMDgj3U")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "6575066703,7282220098").split(",") if x.strip()]
ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else 6575066703
BINANCE_API_BASE_URL = os.getenv("BINANCE_API_BASE_URL", "https://binance-api-yrz4.onrender.com").rstrip("/")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "bg_live_your_merchant_api_key")
CURRENCY_SYMBOL = os.getenv("CURRENCY_SYMBOL", "$")
CURRENCY_NAME = os.getenv("CURRENCY_NAME", "USDT")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@Support")
MIN_DEPOSIT = float(os.getenv("MIN_DEPOSIT", "1.0"))
TELEGRAM_PROXY_URL = os.getenv("TELEGRAM_PROXY_URL", "").strip() or None
TELEGRAM_BASE_URL = os.getenv("TELEGRAM_BASE_URL", "").strip() or None
ORDER_LOG_GROUP_ID = os.getenv("ORDER_LOG_GROUP_ID", "-1003721268860")

# Supabase PostgreSQL Configuration
SUPABASE_HOST = os.getenv("SUPABASE_HOST", "aws-0-ap-northeast-2.pooler.supabase.com")
SUPABASE_PORT = int(os.getenv("SUPABASE_PORT", "6543"))
SUPABASE_USER = os.getenv("SUPABASE_USER", "postgres.uciazyvnymfxnpcsdnbq")
SUPABASE_PASS = os.getenv("SUPABASE_PASS", "Munna1234@@@TTYY")
SUPABASE_DB = os.getenv("SUPABASE_DB", "postgres")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{SUPABASE_USER}:Munna1234%40%40%40TTYY@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}?sslmode=require"
)
DATABASE_PATH = os.getenv("DATABASE_PATH", "nexvora_shop.db")
