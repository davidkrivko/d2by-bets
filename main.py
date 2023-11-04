import asyncio
import datetime
import logging

from database.functions import (
    delete_old_rows,
    create_tables,
    send_bets_to_telegram,
    get_all_active_bets,
    send_telegram_message,
)
from get_data import (
    get_d2by_matches,
    get_fan_sport_league_matches,
    get_fan_sport_leagues,
    get_fan_sport_match_data,
)


async def handle_league(sport_id, leagues, matches):
    leags = await get_fan_sport_leagues(sport_id, leagues)

    tasks = [handle_matches_for_league(leag, matches, sport_id) for leag in leags]

    await asyncio.gather(*tasks)


async def handle_matches_for_league(leag, matches, sport_id):
    mats = await get_fan_sport_league_matches(leag, sport_id, matches)

    tasks = [
        get_fan_sport_match_data(sub_mat, mat["d2by_id"], mat["team_1"], mat["team_2"])
        for mat in mats
        for sub_mat in mat["sub_matches"]
    ]
    tasks += [
        get_fan_sport_match_data(
            mat["id"], mat["d2by_id"], mat["team_1"], mat["team_2"]
        )
        for mat in mats
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
            task = handle_league(1, leagues["Football"], matches)
            tasks.append(task)

        if "Basketball" in leagues:
            task = handle_league(3, leagues["Basketball"], matches)
            tasks.append(task)

        # Cyber sport
        task = handle_league(40, None, matches)
        tasks.append(task)
        await asyncio.gather(*tasks)

        bets = await get_all_active_bets()
        await send_bets_to_telegram(bets)

        i += 1
        if i == 100:
            stop = datetime.datetime.now()
            i = 0
            logging.error(f"100 cycles: {stop} - {start}")


if __name__ == "__main__":
    asyncio.run(main())


