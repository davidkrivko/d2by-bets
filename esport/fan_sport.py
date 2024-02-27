import asyncio
import copy
import datetime
import json

import aiohttp

from betsModel import betsModel
from config import DEFAULT_FAN_HEADERS, FAN_SPORT_DELTA

from database.v2.bets import (
    get_bets_of_match as get_bets_of_match_v2,
    update_bet as update_bet_v2,
)
from database.v2.matches import add_match_to_db

from database.v2.tables import fan_sport_matches

from utils import (
    update_team_name,
    are_teams_similar,
    remove_id_key,
    is_reversed,
    create_fan_sport_url,
    get_team_name,
    add_bet_to_cfs,
)


async def get_fan_sport_leagues(sport: int, match_type):
    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampsZip?sport={sport}&lng=en",
            ssl=False
        ) as resp:
            response = await resp.text()
            leagues = json.loads(response)
    return leagues


async def get_fan_sport_league_matches(league_id, match_type):
    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampZip?lng=en&champ={league_id}",
            ssl=False
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)
    return matches


async def get_fan_sport_match_data(sub_match_id, match_type):
    async with aiohttp.ClientSession(headers=DEFAULT_FAN_HEADERS) as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetGameZip?id={sub_match_id}&lng=en",
            ssl=False
        ) as resp:
            response = await resp.text()
            data = json.loads(response)

    return data


async def collect_fan_sport_leagues(sport_id, match_type, lgs: set = None):
    leagues = await get_fan_sport_leagues(sport_id, match_type)

    if leagues["Success"]:
        leagues = leagues["Value"]

        if leagues:
            if lgs:
                res = {
                    league["LI"]
                    for league in leagues
                    for lg in lgs
                    if lg in league["L"].lower()
                }
            else:
                res = {league["LI"] for league in leagues}

            return res
        else:
            return set()
    else:
        return set()


async def collect_fan_sport_league_matches_v2(
    league_id: int, sport_id: int, mats: dict, match_type: str
):
    match_key = "I" if match_type == "LiveFeed" else "CI"
    matches = await get_fan_sport_league_matches(league_id, match_type)

    if matches["Success"]:
        matches = matches["Value"]
        if not matches:
            return []
        matches = matches["G"]

        res = [
            {
                "id": match[match_key],
                "team_1": update_team_name(match["O1"]),
                "team_2": update_team_name(match["O2"]),
                "start_time": (
                        datetime.datetime.fromtimestamp(match["S"])
                        + datetime.timedelta(hours=FAN_SPORT_DELTA)
                ),
                "d2by_id": mat["id"],
                "sub_matches": [sub[match_key] for sub in match.get("SG", [])]
                if sport_id == 40
                else [],
            }
            for mat in mats
            for match in matches
            if (
                (
                    are_teams_similar(update_team_name(match["O1"]), mat["team_1"])
                    and are_teams_similar(update_team_name(match["O2"]), mat["team_2"])
                )
                or (
                    are_teams_similar(update_team_name(match["O2"]), mat["team_1"])
                    and are_teams_similar(update_team_name(match["O1"]), mat["team_2"])
                )
            )
            and (
                (mat["start_time"] - datetime.timedelta(minutes=30))
                <= datetime.datetime.fromtimestamp(match["S"])
                <= (mat["start_time"] + datetime.timedelta(minutes=30))
            )
        ]

        insert_copy = copy.deepcopy(res)
        await asyncio.gather(
            *[
                add_match_to_db(match, fan_sport_matches)
                for match in list(map(remove_id_key, insert_copy))
            ]
        )

        return res
    else:
        return []


async def compare_bets_v2(
    sub_match: int,
    match_id: int,
    match_type: str,
    sport_id,
):
    bets = await get_fan_sport_match_data(sub_match, match_type)

    if bets["Success"]:
        values = bets["Value"]

        n_map = values.get("P", None)
        if bets:
            fan_team_1 = update_team_name(values["O1"])
            fan_team_2 = update_team_name(values["O2"])

            d2by_bets = await get_bets_of_match_v2(
                match_id, n_map
            )

            bets = values["E"]

            if d2by_bets:
                is_reverse = is_reversed(
                    d2by_bets[0][8],
                    d2by_bets[0][9],
                    fan_team_1,
                    fan_team_2,
                )
            else:
                return

            fan_url = create_fan_sport_url(
                match_type,
                sport_id,
                values.get("LI"),
                values.get("L"),
                values.get("I"),
                values.get("O1"),
                values.get("O2"),
            )
            cfs = {}

            # 0 bet_table.c.id,
            # 1 bet_table.c.d2by_bets,
            # 2 bet_table.c.map_v2,
            # 3 bet_table.c["value"].label("bet_values"),
            # 4 bet_type_table.c.id.label("type_id"),
            # 5 bet_type_table.c.fan_sport_bet_type,
            # 6 bet_type_table.c.fan_sport_bet_type_football,
            # 7 d2by_matches.c.id.label("match_id"),
            # 8 d2by_matches.c.team_1,
            # 9 d2by_matches.c.team_2,
            # 10 bet_table.c.above_bets,
            for d2by_bet in d2by_bets:
                if d2by_bet[5] is not None or d2by_bet[6] is not None:
                    for bet in bets:
                        bet_model = betsModel.get(str(bet["T"]), {})

                        if (
                            bet_model["GN"] == d2by_bet[5] or bet_model["GN"] == d2by_bet[6]
                        ) and n_map == d2by_bet[2]:
                            value = bet.get("P", None)
                            bet_name = get_team_name(bet_model["N"], is_reverse)

                            if is_reverse:
                                if not d2by_bet[3] and not value:
                                    add_bet_to_cfs(
                                        cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                                    )

                                    # if d2by_bet[4] == 18:
                                    #     if str(d2by_bet[10]) not in bet_model["GN"]:
                                    #         add_bet_to_cfs(
                                    #             cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                                    #         )
                                else:
                                    if value:
                                        if abs(value) == d2by_bet[3]:
                                            if "handicap" in bet_model["GN"].lower():
                                                if (
                                                    str(d2by_bet[10]) in bet_model["N"]
                                                    and value == d2by_bet[3]
                                                ) or (
                                                    str(d2by_bet[10]) not in bet_model["N"]
                                                    and value == d2by_bet[3] * -1
                                                ):
                                                    add_bet_to_cfs(
                                                        cfs,
                                                        d2by_bet[0],
                                                        bet_name,
                                                        bet["C"],
                                                        fan_url,
                                                    )
                                            elif "total" not in bet_model["GN"].lower():
                                                add_bet_to_cfs(
                                                    cfs,
                                                    d2by_bet[0],
                                                    bet_name,
                                                    bet["C"],
                                                    fan_url,
                                                )
                            else:
                                if not d2by_bet[3] and not value:
                                    add_bet_to_cfs(
                                        cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                                    )

                                    # if d2by_bet[4] == 18:
                                    #     if str(d2by_bet[10]) in bet_model["GN"]:
                                    #         add_bet_to_cfs(
                                    #             cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                                    #         )
                                else:
                                    if value:
                                        if abs(value) == d2by_bet[3]:
                                            if "handicap" in bet_model["GN"].lower():
                                                if (
                                                    str(d2by_bet[10]) in bet_model["N"]
                                                    and value == d2by_bet[3] * -1
                                                ) or (
                                                    str(d2by_bet[10]) not in bet_model["N"]
                                                    and value == d2by_bet[3]
                                                ):
                                                    add_bet_to_cfs(
                                                        cfs,
                                                        d2by_bet[0],
                                                        bet_name,
                                                        bet["C"],
                                                        fan_url,
                                                    )
                                            elif "total" not in bet_model["GN"].lower():
                                                add_bet_to_cfs(
                                                    cfs,
                                                    d2by_bet[0],
                                                    bet_name,
                                                    bet["C"],
                                                    fan_url,
                                                )
                            if (
                                "total" in bet_model["GN"].lower()
                                and "handicap" not in bet_model["GN"].lower()
                            ):
                                if value == d2by_bet[3]:
                                    bet_name = "Over" if "Over" in bet_name else "Under"
                                    add_bet_to_cfs(
                                        cfs, d2by_bet[0], bet_name, bet["C"], fan_url
                                    )

            tasks = [update_bet_v2(cf) for cf in cfs.values()]
            await asyncio.gather(*tasks)
