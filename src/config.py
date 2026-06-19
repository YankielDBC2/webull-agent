import os
from dotenv import load_dotenv

load_dotenv()

# Webull Test Credentials
WEBULL_APP_KEY = os.getenv("WEBULL_APP_KEY", "a88f2efed4dca02b9bc1a3cecbc35dba")
WEBULL_APP_SECRET = os.getenv("WEBULL_APP_SECRET", "c2895b3526cc7c7588758351ddf425d6")
WEBULL_ENVIRONMENT = os.getenv("WEBULL_ENVIRONMENT", "uat")
WEBULL_REGION_ID = os.getenv("WEBULL_REGION_ID", "us")
WEBULL_API_HOST = os.getenv("WEBULL_API_HOST", "us-openapi-alb.uat.webullbroker.com")
WEBULL_API_BASE = f"https://{WEBULL_API_HOST}"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

# Bot Settings
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "5"))
REPORT_INTERVAL_MINUTES = int(os.getenv("REPORT_INTERVAL_MINUTES", "5"))
HOURLY_SUMMARY = os.getenv("HOURLY_SUMMARY", "true").lower() == "true"

# Watchlist
WATCHLIST = [
    "SOFI", "F", "NIO", "SNAP", "AAL",
    "CCL", "RIVN", "AMC", "RIOT", "MARA",
]

# Alert thresholds
ALERT_VOLUME_MULTIPLIER = float(os.getenv("ALERT_VOLUME_MULTIPLIER", "2.0"))
ALERT_SPREAD_PCT = float(os.getenv("ALERT_SPREAD_PCT", "1.0"))
ALERT_PRICE_CHANGE_PCT = float(os.getenv("ALERT_PRICE_CHANGE_PCT", "5.0"))
