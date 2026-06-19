import hashlib
import hmac
import base64
import json
import uuid
import urllib.parse
from datetime import datetime, timezone

import requests

from src.config import WEBULL_APP_KEY, WEBULL_APP_SECRET, WEBULL_API_HOST


class WebullClient:
    def __init__(self, app_key=None, app_secret=None, host=None):
        self.app_key = app_key or WEBULL_APP_KEY
        self.app_secret = app_secret or WEBULL_APP_SECRET
        self.host = host or WEBULL_API_HOST
        self.base_url = f"https://{self.host}"

    def _generate_signature(self, path, query_params, body_string, timestamp, nonce):
        signing_headers = {
            "x-app-key": self.app_key,
            "x-timestamp": timestamp,
            "x-signature-algorithm": "HMAC-SHA1",
            "x-signature-version": "1.0",
            "x-signature-nonce": nonce,
            "host": self.host,
        }
        all_params = {}
        all_params.update(query_params or {})
        all_params.update(signing_headers)

        str1 = "&".join(f"{k}={all_params[k]}" for k in sorted(all_params.keys()))

        if body_string:
            str2 = hashlib.md5(body_string.encode("utf-8")).hexdigest().upper()
            str3 = f"{path}&{str1}&{str2}"
        else:
            str3 = f"{path}&{str1}"

        encoded_string = urllib.parse.quote(str3, safe="")
        signing_key = f"{self.app_secret}&"

        signature = base64.b64encode(
            hmac.new(
                signing_key.encode("utf-8"),
                encoded_string.encode("utf-8"),
                hashlib.sha1,
            ).digest()
        ).decode("utf-8")

        return signature

    def _headers(self, path, query_params=None, body_string=None):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        nonce = uuid.uuid4().hex
        signature = self._generate_signature(
            path, query_params, body_string, timestamp, nonce
        )
        return {
            "x-app-key": self.app_key,
            "x-timestamp": timestamp,
            "x-signature": signature,
            "x-signature-algorithm": "HMAC-SHA1",
            "x-signature-version": "1.0",
            "x-signature-nonce": nonce,
            "x-version": "v2",
        }

    def _get(self, path, params=None):
        params = params or {}
        headers = self._headers(path, params)
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        return resp

    def _post(self, path, params=None, data=None):
        params = params or {}
        body_string = json.dumps(data, separators=(",", ":")) if data else None
        headers = self._headers(path, params, body_string)
        headers["Content-Type"] = "application/json"
        url = f"{self.base_url}{path}"
        resp = requests.post(
            url, headers=headers, params=params, data=body_string, timeout=10
        )
        return resp

    def get_stock_snapshot(self, symbols):
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        return self._get(
            "/openapi/market-data/stock/snapshot",
            params={
                "symbols": symbols,
                "category": "US_STOCK",
                "extend_hour_required": "false",
                "overnight_required": "false",
            },
        )

    def get_stock_quotes(self, symbols, depth=1):
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        return self._get(
            "/openapi/market-data/stock/quotes",
            params={"symbols": symbols, "depth": str(depth)},
        )

    def get_stock_bars(self, symbol, granularity="M5", count=20):
        return self._get(
            "/openapi/market-data/stock/bars",
            params={
                "symbol": symbol,
                "granularity": granularity,
                "count": str(count),
            },
        )

    def get_top_active(self, rank_by="volume", limit=20):
        return self._get(
            "/openapi/market-data/screener/top-active",
            params={"rank_by": rank_by, "limit": str(limit)},
        )

    def get_gainers_losers(self, direction="DESC", limit=10):
        return self._get(
            "/openapi/market-data/screener/gainers-losers",
            params={
                "order": "CHANGE_RATIO",
                "direction": direction,
                "limit": str(limit),
            },
        )

    def get_account_list(self):
        return self._get("/openapi/account/list")

    def health_check(self):
        try:
            resp = self.get_account_list()
            return resp.status_code, resp.json() if resp.ok else resp.text
        except Exception as e:
            return None, str(e)
