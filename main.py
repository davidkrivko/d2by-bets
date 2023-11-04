import asyncio
import datetime

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


# 1 - Football
# 3 - Basketball
# 40 - Cyber sport
async def main():
    i = 0

    while True:
        if i == 0:
            await delete_old_rows()

        start = datetime.datetime.now()

        leagues, matches = await get_d2by_matches()

        tasks = []
        if "Football" in leagues:
            task = handle_league(1, leagues["Football"], matches)
            tasks.append(task)

        if "Basketball" in leagues:
            task = handle_league(3, leagues["Basketball"], matches)
            tasks.append(task)

        # For the separate league with id 40
        task = handle_league(40, None, matches)
        tasks.append(task)
        await asyncio.gather(*tasks)

        bets = await get_all_active_bets()
        await send_bets_to_telegram(bets)

        i += 1
        if i == 100:
            i = 0

        stop = datetime.datetime.now()
        print(stop - start)


async def main2():
    leagues, mats = await get_d2by_matches()

    leagues = await get_fan_sport_leagues(40)
    for league in leagues:
        matches = await get_fan_sport_league_matches(league, 40, mats)

        for match in matches:
            bets = await get_fan_sport_match_data(
                match["id"], match["d2by_id"], match["team_1"], match["team_2"]
            )


if __name__ == "__main__":
    asyncio.run(main())

