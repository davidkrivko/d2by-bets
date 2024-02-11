import asyncio
import os
import sys

current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of the current script's directory
parent_directory = os.path.dirname(current_directory)
root_directory = os.path.dirname(parent_directory)

# Add the parent directory to sys.path
sys.path.append(root_directory)


from database.v1.matches import get_d2by_matches
from sport.fan_sport import (
    collect_fan_sport_leagues,
    collect_fan_sport_league_matches,
)


async def handle_league(sport_id, leagues, matches, match_type):
    leags = await collect_fan_sport_leagues(sport_id, match_type, leagues)

    if leags:
        tasks = [
            handle_matches_for_league(leag, matches, sport_id, match_type) for leag in leags
        ]

        await asyncio.gather(*tasks)


async def handle_matches_for_league(leag, matches, sport_id, match_type):
    await collect_fan_sport_league_matches(leag, sport_id, matches, match_type)


async def collect_fan_sport_matches():
    leagues, matches = await get_d2by_matches()

    await handle_league(1, leagues["Football"], matches, "LineFeed")
    await handle_league(3, leagues["Basketball"], matches, "LineFeed")


asyncio.run(collect_fan_sport_matches())
