import asyncio

from simplegmail import Gmail
from config import USERNAME, PASSWORD
from login.api import get_balance, get_token

GMAIL_CLIENT = Gmail()
AUTH_TOKEN = get_token(USERNAME, PASSWORD, GMAIL_CLIENT)


def bal():
    asyncio.run(get_balance(AUTH_TOKEN))


bal()
