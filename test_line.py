import requests

import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual values or ensure they are correct in app.py
# For this test, please paste them here directly to verify.
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
USER_ID = os.getenv('LINE_TEST_USER_ID')

def test_line_push():
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'to': USER_ID,
        'messages': [
            {
                'type': 'text',
                'text': 'これはテスト通知です！🚰 LINE連携は正常に動作しています。'
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("Success! Message sent to LINE.")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_line_push()
