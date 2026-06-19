import asyncio
from datetime import datetime

import pytz
from telegram import Bot
from telegram.error import TelegramError

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID

ET = pytz.timezone("US/Eastern")


class TelegramReporter:
    def __init__(self, token=None, channel_id=None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.channel_id = channel_id or TELEGRAM_CHANNEL_ID
        self.bot = None
        self._ready = bool(self.token and self.channel_id)

    async def _get_bot(self):
        if self.bot is None and self._ready:
            self.bot = Bot(token=self.token)
        return self.bot

    async def send(self, text, parse_mode="HTML"):
        if not self._ready:
            print(f"[TELEGRAM DISABLED] {text[:100]}")
            return None
        try:
            bot = await self._get_bot()
            if bot:
                return await bot.send_message(
                    chat_id=self.channel_id, text=text, parse_mode=parse_mode
                )
        except TelegramError as e:
            print(f"[TELEGRAM ERROR] {e}")

    async def send_status_report(self, snapshots):
        now = datetime.now(ET).strftime("%H:%M ET")
        lines = [f"<b>📊 STATUS {now}</b>", "━" * 20]

        for s in snapshots:
            symbol = s.get("symbol", "?")
            price = float(s.get("price", 0))
            change = float(s.get("change", 0))
            change_ratio = float(s.get("change_ratio", 0))
            volume = int(float(s.get("volume", 0)))
            bid = s.get("_bid", 0)
            ask = s.get("_ask", 0)
            spread = s.get("_spread", 0)

            arrow = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            vol_str = f"{volume / 1e6:.1f}M" if volume > 1e6 else str(volume)

            lines.append(
                f"{arrow} <b>{symbol}</b>  ${price:.2f}  "
                f"{change_ratio * 100:+.2f}%  Vol:{vol_str}"
            )
            if bid and ask:
                lines.append(f"   Bid:{bid:.2f}  Ask:{ask:.2f}  Spread:${spread:.4f}")

        lines.append("━" * 20)
        await self.send("\n".join(lines))

    async def send_alert(self, alert_type, symbol, details):
        emoji = {"volume": "📊", "spread": "⚠️", "price": "🚨", "trend": "📈"}
        em = emoji.get(alert_type, "📢")

        text = f"{em} <b>ALERTA {alert_type.upper()} — {symbol}</b>\n{details}"
        await self.send(text)

    async def send_hourly_summary(self, snapshots):
        now = datetime.now(ET).strftime("%H:00 ET")
        lines = [f"<b>📈 RESUMEN {now}</b>", "━" * 20]

        sorted_change = sorted(
            snapshots, key=lambda s: float(s.get("change_ratio", 0)), reverse=True
        )
        sorted_volume = sorted(
            snapshots, key=lambda s: float(s.get("volume", 0)), reverse=True
        )

        lines.append("<b>Top Gainers:</b>")
        for s in sorted_change[:3]:
            lines.append(
                f"  🟢 {s['symbol']} {float(s['change_ratio']) * 100:+.2f}%"
            )

        lines.append("<b>Top Losers:</b>")
        for s in sorted_change[-3:]:
            lines.append(
                f"  🔴 {s['symbol']} {float(s['change_ratio']) * 100:+.2f}%"
            )

        lines.append(f"<b>Mayor Volumen:</b> {sorted_volume[0]['symbol']}")
        await self.send("\n".join(lines))

    async def send_startup(self, watchlist):
        text = (
            f"🤖 <b>BOT INICIADO</b>\n"
            f"Monitoreando {len(watchlist)} stocks:\n"
            f"{', '.join(watchlist)}\n"
            f"Entorno: TEST (UAT)"
        )
        await self.send(text)

    async def send_shutdown(self, reason=""):
        text = f"🛑 <b>BOT DETENIDO</b>"
        if reason:
            text += f"\nMotivo: {reason}"
        await self.send(text)
