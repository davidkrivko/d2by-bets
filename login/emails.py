import datetime
import requests

from simplegmail.query import construct_query
from bs4 import BeautifulSoup

from config import TELEGRAM_BOT, CHAT_ID


def send_telegram_message_sync(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}

    resp = requests.post(telegram_url, data=data)

    return resp.status_code


def get_verification_code(time, gmail_client):
    current_time = datetime.datetime.now().strftime("%Y/%m/%d")

    is_new = True

    i = 0
    while is_new:
        i += 1

        query_params = {
            "unread": True,
            "sender": "noreply@d2by.com",
            "after": current_time
        }
        messages = gmail_client.get_messages(query=construct_query(query_params))
        if messages:
            message = messages[0]

            sent_at = datetime.datetime.fromisoformat(message.date)
            sent_at = sent_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if sent_at > time:
                is_new = False

        if i == 10:
            send_telegram_message_sync("Email is not coming!")
            return None

    html = message.html
    soup = BeautifulSoup(html, "html.parser")
    font_element = soup.find("font", {"color": "#ff9900", "size": "6"})
    verification_code = font_element.get_text()

    return str(verification_code)
