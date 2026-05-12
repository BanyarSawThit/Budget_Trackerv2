import time

import requests
from decouple import config

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
GROUP_CHAT_ID = config('TELEGRAM_GROUP_CHAT_ID')

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id,'text': message,'parse_mode': 'HTML'}

    for attempt in range(2):
        try:
            requests.post(url, data=data, timeout=5)
            return True
        except Exception:
            if attempt == 0:
                time.sleep(5)
    return False

def notify_user(added_by_username, amount, category, description, budget):
        msg = (
            f"<b>{added_by_username}'s</b> Budget: ฿{budget}\n"
            f"{category}: ฿{amount}\n"
            f"{description or '-'}\n"
        )
        return send_telegram(GROUP_CHAT_ID, msg)