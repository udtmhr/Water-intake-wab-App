import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_sensor_data(amount):
    url = f"{BASE_URL}/intake"
    data = {
        "amount": amount,
        "timestamp": time.time()
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Success: Sent {amount}ml. Response: {response.json()}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    print("Simulating sensor data...")
    # Simulate drinking 200ml
    test_sensor_data(200)
