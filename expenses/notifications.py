import threading
import time

import requests
from decouple import config

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
GROUP_CHAT_ID = config('TELEGRAM_GROUP_CHAT_ID')

def _send_with_retry(url, data):
    for attempt in range(2):
        try:
            requests.post(url, data=data, timeout=5)
            return
        except Exception:
            if attempt == 0:
                time.sleep(7)

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id,'text': message,'parse_mode': 'HTML'}

    thread = threading.Thread(target=_send_with_retry, args=(url, data))
    thread.daemon = True
    thread.start()

def notify_user(added_by_username, amount, category, description, budget):
        msg = (
            f"<b>{added_by_username}'s</b> Balance: ฿{budget}\n"
            f"{category}: ฿{amount}\n"
            f"{description or '-'}\n"
        )
        send_telegram(GROUP_CHAT_ID, msg)