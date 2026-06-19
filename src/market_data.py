import time
from datetime import datetime
from collections import defaultdict

from src.config import (
    WATCHLIST,
    POLL_INTERVAL_SECONDS,
    ALERT_VOLUME_MULTIPLIER,
    ALERT_SPREAD_PCT,
    ALERT_PRICE_CHANGE_PCT,
)


class MarketDataEngine:
    def __init__(self, webull_client):
        self.client = webull_client
        self.snapshots = {}  # symbol -> latest snapshot
        self.quotes = {}  # symbol -> latest quote
        self.price_history = defaultdict(list)  # symbol -> [(ts, price), ...]
        self.volume_history = defaultdict(list)  # symbol -> [(ts, volume), ...]
        self.avg_volume = {}  # symbol -> avg volume (estimated)
        self.last_report_time = 0
        self.last_summary_time = 0

    def update(self):
        symbols_str = ",".join(WATCHLIST)

        # Fetch snapshots (batch)
        try:
            resp = self.client.get_stock_snapshot(WATCHLIST)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data:
                        sym = item.get("symbol")
                        if sym:
                            self.snapshots[sym] = item
                            ts = datetime.now()
                            price = float(item.get("price", 0))
                            volume = int(float(item.get("volume", 0)))
                            self.price_history[sym].append((ts, price))
                            self.volume_history[sym].append((ts, volume))
                            if len(self.price_history[sym]) > 720:
                                self.price_history[sym] = self.price_history[sym][-720:]
                            if len(self.volume_history[sym]) > 100:
                                self.volume_history[sym] = self.volume_history[sym][-100:]
            else:
                print(f"[WEBULL ERROR] Snapshot: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"[WEBULL EXCEPTION] Snapshot: {e}")

        # Fetch quotes (batch)
        try:
            resp = self.client.get_stock_quotes(WATCHLIST, depth=1)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data:
                        sym = item.get("symbol")
                        if sym and sym in self.snapshots:
                            bid = float(item.get("bid_price", 0) or 0)
                            ask = float(item.get("ask_price", 0) or 0)
                            self.snapshots[sym]["_bid"] = bid
                            self.snapshots[sym]["_ask"] = ask
                            self.snapshots[sym]["_spread"] = round(ask - bid, 4) if bid and ask else 0
            else:
                print(f"[WEBULL ERROR] Quotes: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"[WEBULL EXCEPTION] Quotes: {e}")

    def get_snapshots(self):
        return [self.snapshots.get(s, {"symbol": s}) for s in WATCHLIST]

    def check_alerts(self):
        alerts = []

        for sym in WATCHLIST:
            snap = self.snapshots.get(sym)
            if not snap:
                continue

            price = float(snap.get("price", 0))
            volume = int(float(snap.get("volume", 0)))
            change_ratio = float(snap.get("change_ratio", 0))
            spread = snap.get("_spread", 0)

            # Volume alert
            avg_vol = self.avg_volume.get(sym, volume)
            if avg_vol > 0 and volume > avg_vol * ALERT_VOLUME_MULTIPLIER:
                alerts.append((
                    "volume",
                    sym,
                    f"Volumen: {volume / 1e6:.1f}M ({volume / avg_vol:.1f}x promedio)"
                ))

            # Spread alert
            if price > 0 and spread > 0:
                spread_pct = (spread / price) * 100
                if spread_pct > ALERT_SPREAD_PCT:
                    alerts.append((
                        "spread",
                        sym,
                        f"Spread: ${spread:.4f} ({spread_pct:.2f}% del precio)"
                    ))

            # Price alert
            if abs(change_ratio * 100) > ALERT_PRICE_CHANGE_PCT:
                alerts.append((
                    "price",
                    sym,
                    f"Cambio: {change_ratio * 100:+.2f}% — Precio: ${price:.2f}"
                ))

            # Update rolling average volume
            if volume > 0:
                if sym not in self.avg_volume:
                    self.avg_volume[sym] = volume
                else:
                    self.avg_volume[sym] = self.avg_volume[sym] * 0.9 + volume * 0.1

        return alerts
