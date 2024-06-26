import asyncio
import datetime
import logging

from simplegmail import Gmail

from config import USERNAME, PASSWORD
from login.api import get_token, get_balance

from esport.script import v2_script
from sport.script import v1_script


async def update_all_bets():
    i = 0

    GMAIL_CLIENT = Gmail()
    AUTH_TOKEN = get_token(USERNAME, PASSWORD, GMAIL_CLIENT)

    while True:
        start = datetime.datetime.now()

        tasks = [
            v1_script(),
            v2_script("LineFeed", AUTH_TOKEN)
            # v2_script("LiveFeed", AUTH_TOKEN),
        ]

        await asyncio.gather(*tasks)

        i += 1
        stop = datetime.datetime.now()
        logging.error(stop - start)

        await asyncio.sleep(2)
