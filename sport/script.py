import asyncio

from database.v1.bets import get_all_active_bets
from database.v1.matches import get_fan_sport_matches
from sport.api import collect_d2by_sport_matches
from sport.fan_sport import (
    collect_fan_sport_match_data,
)
from telegram import send_bets_to_telegram


async def v1_script():
    await collect_d2by_sport_matches()

    fan_mats = await get_fan_sport_matches()

    tasks = [
        collect_fan_sport_match_data(sub_mat, mat["d2by_id"], "LineFeed", mat["sport_id"])
        for mat in fan_mats
        for sub_mat in mat["fan_ids"].split(",")
    ]

    await asyncio.gather(*tasks)

    bets = await get_all_active_bets()
    await send_bets_to_telegram(bets)
