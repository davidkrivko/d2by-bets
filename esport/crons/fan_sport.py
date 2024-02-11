import os
import sys
import asyncio

current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of the current script's directory
parent_directory = os.path.dirname(current_directory)
root_directory = os.path.dirname(parent_directory)

# Add the parent directory to sys.path
sys.path.append(root_directory)


from database.v2.matches import get_d2by_line_matches, get_d2by_live_matches
from esport.fan_sport import (
    collect_fan_sport_leagues,
    collect_fan_sport_league_matches_v2,
)


async def collect_fan_sport_matches():
    matches = await get_d2by_line_matches()
    matches += await get_d2by_live_matches()

    await get_d2by_line_matches()
    leags = await collect_fan_sport_leagues(40, "LineFeed")

    tasks = [
        collect_fan_sport_league_matches_v2(leag, 40, matches, "LineFeed") for leag in leags
    ]

    await asyncio.gather(*tasks)


asyncio.run(collect_fan_sport_matches())
