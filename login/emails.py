import datetime

from simplegmail.query import construct_query
from bs4 import BeautifulSoup


def get_verification_code(time):
    from config import GMAIL_CLIENT

    is_new = True
    while is_new:
        query_params = {"unread": True, "sender": "noreply@d2by.com"}
        messages = GMAIL_CLIENT.get_messages(query=construct_query(query_params))
        if messages:
            message = messages[0]

            sent_at = datetime.datetime.fromisoformat(message.date)
            sent_at = sent_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            if sent_at > time:
                is_new = False

    html = message.html
    soup = BeautifulSoup(html, "html.parser")
    font_element = soup.find("font", {"color": "#ff9900", "size": "6"})
    verification_code = font_element.get_text()

    return str(verification_code)
