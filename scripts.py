import datetime
import logging

from simplegmail import Gmail

from config import USERNAME, PASSWORD
from login.api import get_token

from esport.script import v2_script
from sport.script import v1_script


async def update_all_bets():
    i = 0

    GMAIL_CLIENT = Gmail()
    AUTH_TOKEN = get_token(USERNAME, PASSWORD, GMAIL_CLIENT)

    while True:
        start = datetime.datetime.now()

        await v1_script()
        await v2_script("line", AUTH_TOKEN)

        await v2_script("live", AUTH_TOKEN)

        i += 1
        stop = datetime.datetime.now()
        logging.error(stop - start)
