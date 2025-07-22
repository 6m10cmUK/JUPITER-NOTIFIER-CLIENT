import requests
import sys

# テスト用スクリプト
url = "https://jupiter-system--jupiter-system--r6m10cms-team.p1.northflank.app"

print(f"Testing connection to: {url}")

try:
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print("\nHTTP connection successful!")
    print("\nTry WebSocket URL:")
    print("wss://jupiter-system--jupiter-system--r6m10cms-team.p1.northflank.app")
except Exception as e:
    print(f"Error: {e}")
    print("\nCannot connect to the server. Please check:")
    print("1. The Northflank URL is correct")
    print("2. The service is running")
    print("3. Your internet connection")