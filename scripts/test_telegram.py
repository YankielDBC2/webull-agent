import sys
import os
sys.path.insert(0, ".")

# Force load .env
from dotenv import load_dotenv
load_dotenv()

# Override with explicit credentials
from src.webull_client import WebullClient
from src.telegram_reporter import TelegramReporter
import asyncio

async def test_telegram():
    reporter = TelegramReporter()
    text = "TEST BOT - Conexion establecida\nWebull test env: OK\nAAPL: funcionando"
    await reporter.send(f"<b>TEST BOT</b>\n{text}")

asyncio.run(test_telegram())
