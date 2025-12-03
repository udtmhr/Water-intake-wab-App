import requests

def calculate_daily_goal(weight, age):
    """
    Calculate daily water intake goal based on weight and age.
    Simple formula: 
    - < 30 years: weight * 40
    - 30-55 years: weight * 35
    - > 55 years: weight * 30
    """
    if age < 30:
        return int(weight * 40)
    elif age <= 55:
        return int(weight * 35)
    else:
        return int(weight * 30)

def send_line_message(token, user_id, message):
    """
    Send a push message to a LINE user.
    """
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'to': user_id,
        'messages': [
            {
                'type': 'text',
                'text': message
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print("LINE notification sent successfully.")
            return True
        else:
            print(f"Failed to send LINE notification: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending LINE notification: {e}")
        return False
