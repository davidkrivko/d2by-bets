import asyncio
import datetime
import logging

from database.functions.bets import get_all_active_bets
from database.functions.matches import delete_old_rows

from parcing.fan_sport import (
    collect_fan_sport_match_data,
    collect_fan_sport_leagues,
    collect_fan_sport_league_matches,
)
from parcing.d2by import get_d2by_matches
from parcing.telegram import send_bets_to_telegram


async def handle_league(sport_id, leagues, matches, match_type):
    leags = await collect_fan_sport_leagues(sport_id, match_type, leagues)

    if leags:
        tasks = [
            handle_matches_for_league(leag, matches, sport_id, match_type) for leag in leags
        ]

        await asyncio.gather(*tasks)


async def handle_matches_for_league(leag, matches, sport_id, match_type):
    mats = await collect_fan_sport_league_matches(leag, sport_id, matches, match_type)

    if mats:
        tasks = [
            collect_fan_sport_match_data(
                sub_mat, mat["d2by_id"], match_type
            )
            for mat in mats
            for sub_mat in (mat["sub_matches"] + [mat["id"]])
        ]

        await asyncio.gather(*tasks)


async def main():
    i = 0

    while True:
        if i == 0:
            start = datetime.datetime.now()
            await delete_old_rows()

        leagues, matches = await get_d2by_matches()

        tasks = []
        if "Football" in leagues:
            task = handle_league(1, leagues["Football"], matches, "LineFeed")
            tasks.append(task)

        if "Basketball" in leagues:
            task = handle_league(3, leagues["Basketball"], matches, "LineFeed")
            tasks.append(task)

        # Cyber sport Line
        task = handle_league(40, None, matches, "LineFeed")
        tasks.append(task)

        # Live
        task = handle_league(40, None, matches, "LiveFeed")
        tasks.append(task)

        await asyncio.gather(*tasks)

        bets = await get_all_active_bets()
        await send_bets_to_telegram(bets)

        i += 1
        if i == 10:
            stop = datetime.datetime.now()
            i = 0
            logging.error(f"100 cycles: {stop - start}")
