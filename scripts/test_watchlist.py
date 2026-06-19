import sys
sys.path.insert(0, ".")

from src.webull_client import WebullClient

c = WebullClient()
symbols = ["SOFI", "F", "NIO", "SNAP", "AAL", "CCL", "RIVN", "AMC", "RIOT", "MARA"]

print("Fetching snapshots...")
resp = c.get_stock_snapshot(symbols)
if resp.status_code == 200:
    data = resp.json()
    print(f"{'Symbol':<6} {'Price':>8} {'Change':>8} {'Volume':>10}")
    print("-" * 38)
    for s in data:
        sym = s["symbol"]
        price = float(s["price"])
        change = float(s["change_ratio"]) * 100
        vol = int(float(s["volume"])) // 1000000
        print(f"{sym:<6} ${price:>7.2f} {change:>+7.2f}% {vol:>7}M")
else:
    print(f"Error: {resp.status_code}")
    print(resp.text[:300])
