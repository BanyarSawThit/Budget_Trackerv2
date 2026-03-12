import requests
from decouple import config


TELEGRAM_TOKEN = config('TELEGRAM_BOT_TOKEN')

USER_CHAT_IDS = {
    config('TELEGRAM_USER1_USERNAME'): config('TELEGRAM_CHAT_ID_USER1'),
    config('TELEGRAM_USER2_USERNAME'): config('TELEGRAM_CHAT_ID_USER2')
}

def send_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    })

def notify_other_user(added_by_username, amount, category, description):
    for username, chat_id in USER_CHAT_IDS.items():
        if username != added_by_username:
            msg = (
                f"<b>{added_by_username}\n</b>"
                f"{category} "
                f"{amount:}$\n"
                f"{description or '-'}"
            )
            send_telegram(chat_id, msg)