import asyncio

from database.v2.bets import get_all_active_bets, is_shown_update
from database.v2.matches import (
    get_d2by_live_matches,
    get_d2by_line_matches,
    get_fan_sport_live_matches,
    get_fan_sport_line_matches,
)

from esport.fan_sport import compare_bets_v2
from esport.api import get_bets_of_d2by_match
from telegram import send_match_to_telegram_v2


def query_compare_bet_cfs_v2(d2by_bets, fan_bets):
    for key in d2by_bets:
        if key in fan_bets:
            value1 = d2by_bets[key]
            value2 = fan_bets[key]

            if value1 / value2 >= 1.15 or value1 / value2 <= 0.85:
                return True

    return False


async def v2_script(time: str):
    if time == "live":
        matches = await get_d2by_live_matches()
        mats = await get_fan_sport_live_matches()
    else:
        matches = await get_d2by_line_matches()
        mats = await get_fan_sport_line_matches()

    tasks = [get_bets_of_d2by_match(match) for match in matches]
    await asyncio.gather(*tasks)

    tasks = []
    for mat in mats:
        tasks.extend([
            compare_bets_v2(sub_mat, mat["d2by_id"], "LineFeed", 40)
            for sub_mat in mat["fan_ids"].split(",")
        ])

    await asyncio.gather(*tasks)

    all_bets = await get_all_active_bets()

    bets = []
    for bet in all_bets:
        if query_compare_bet_cfs_v2(bet[1], bet[2]):
            bets.append(list(bet))

    sended_ids = await asyncio.gather(*[send_match_to_telegram_v2(bets_data) for bets_data in bets])

    await is_shown_update(sended_ids)
