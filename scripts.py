import datetime
import logging

from esport.script import v2_script
from sport.script import v1_script


async def update_all_bets():
    i = 0

    while True:
        start = datetime.datetime.now()

        if i == 5:
            await v1_script()
            await v2_script("line")
            i = 0

        await v2_script("live")

        i += 1
        stop = datetime.datetime.now()
        logging.error(stop - start)
