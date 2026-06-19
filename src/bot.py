#!/usr/bin/env python
"""
Webull Agent Bot — Paper Trading Monitor
Monitorea 10 stocks en tiempo real y envia reportes a Telegram.
"""

import asyncio
import signal
import sys
import time
from datetime import datetime

from src.config import (
    WATCHLIST,
    POLL_INTERVAL_SECONDS,
    REPORT_INTERVAL_MINUTES,
    HOURLY_SUMMARY,
)
from src.webull_client import WebullClient
from src.market_data import MarketDataEngine
from src.telegram_reporter import TelegramReporter


class Bot:
    def __init__(self):
        self.client = WebullClient()
        self.engine = MarketDataEngine(self.client)
        self.reporter = TelegramReporter()
        self.running = False

    async def start(self):
        self.running = True
        print(f"🤖 Bot iniciado — {len(WATCHLIST)} stocks")
        print(f"⏱️  Poll: cada {POLL_INTERVAL_SECONDS}s | Report: cada {REPORT_INTERVAL_MINUTES}min")

        # Test Webull connection
        status, data = self.client.health_check()
        if status == 200:
            print(f"✅ Webull conectado (test env)")
        else:
            print(f"⚠️  Webull: {status} — {data}")

        # Startup message
        await self.reporter.send_startup(WATCHLIST)

        # Main loop
        while self.running:
            try:
                self._tick()
                await self._check_alerts()
                await self._check_reports()
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                await asyncio.sleep(POLL_INTERVAL_SECONDS)

        await self.reporter.send_shutdown("Manual")

    def _tick(self):
        self.engine.update()

    async def _check_alerts(self):
        alerts = self.engine.check_alerts()
        for alert_type, symbol, details in alerts:
            await self.reporter.send_alert(alert_type, symbol, details)

    async def _check_reports(self):
        now = time.time()

        if now - self.engine.last_report_time >= REPORT_INTERVAL_MINUTES * 60:
            self.engine.last_report_time = now
            snapshots = self.engine.get_snapshots()
            await self.reporter.send_status_report(snapshots)

        if HOURLY_SUMMARY and now - self.engine.last_summary_time >= 3600:
            self.engine.last_summary_time = now
            snapshots = self.engine.get_snapshots()
            await self.reporter.send_hourly_summary(snapshots)

    def stop(self):
        self.running = False


async def main():
    bot = Bot()

    def shutdown(sig=None, frame=None):
        print("\n🛑 Apagando...")
        bot.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
