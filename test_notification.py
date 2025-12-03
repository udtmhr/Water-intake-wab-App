import requests
from datetime import datetime, timedelta

BASE_URL = 'http://127.0.0.1:5000/api'

def simulate_old_intake():
    # 1. Reset existing data to ensure our "old" record is the latest
    reset_url = f"{BASE_URL}/intake"
    try:
        requests.delete(reset_url)
        print("Reset existing water logs.")
    except Exception as e:
        print(f"Warning: Failed to reset logs: {e}")

    # 2. Calculate a timestamp for 3 hours ago
    three_hours_ago = datetime.utcnow() - timedelta(hours=3)
    timestamp = three_hours_ago.timestamp()

    url = f"{BASE_URL}/intake"
    data = {
        "amount": 100,
        "timestamp": timestamp
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Success: Sent 100ml with timestamp {three_hours_ago} (3 hours ago).")
            print("The browser should receive a notification within 5 seconds (on next poll).")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    print("Simulating old water intake to trigger notification...")
    simulate_old_intake()
