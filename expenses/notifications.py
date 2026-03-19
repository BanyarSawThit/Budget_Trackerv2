import requests
from decouple import config

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
GROUP_CHAT_ID = config('TELEGRAM_GROUP_CHAT_ID')


def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    })

def notify_other_user(added_by_username, amount, category, description):
        msg = (
            f"<b>{added_by_username}</b> | {category} | -{amount}\n"
            f"\t {description or '-'}"
        )
        send_telegram(GROUP_CHAT_ID, msg)