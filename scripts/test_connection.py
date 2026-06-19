import sys
sys.path.insert(0, ".")

from src.webull_client import WebullClient

print("Testing Webull API connection...")
c = WebullClient()

# Test account list
print("\n--- Account List ---")
status, data = c.health_check()
print(f"Status: {status}")
if isinstance(data, list):
    print(f"Accounts found: {len(data)}")
    for a in data[:3]:
        print(f"  ID: {a.get('account_id', '?')[:20]}... Type: {a.get('account_type', '?')}")
elif isinstance(data, dict):
    print(f"Error response: {list(data.keys())}")
else:
    print(f"Raw: {str(data)[:300]}")

# Test snapshot
print("\n--- Stock Snapshot (AAPL) ---")
resp = c.get_stock_snapshot(["AAPL"])
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    if isinstance(data, list) and len(data) > 0:
        s = data[0]
        print(f"Symbol: {s.get('symbol')}")
        print(f"Price: {s.get('price')}")
        print(f"Volume: {s.get('volume')}")
        print(f"Change: {s.get('change_ratio')}")
    else:
        print(f"Data: {data}")
else:
    print(f"Error: {resp.text[:300]}")
