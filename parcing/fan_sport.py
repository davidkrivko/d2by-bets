import asyncio
import copy
import datetime
import json

import aiohttp

from parcing.betsModel import betsModel
from database.functions.bets import (
    get_bets_of_match,
    update_bet,
)
from database.functions.matches import add_match_to_db

from database.tables import fan_sport_matches
from parcing.utils import (
    update_team_name,
    are_teams_similar,
    remove_id_key,
    is_reversed,
)


async def get_fan_sport_leagues(sport: int, match_type):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampsZip?sport={sport}&lng=en"
        ) as resp:
            response = await resp.text()
            leagues = json.loads(response)
    return leagues


async def get_fan_sport_league_matches(league_id, match_type):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetChampZip?lng=en&champ={league_id}"
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)
    return matches


async def get_fan_sport_match_data(sub_match_id, match_type):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/{match_type}/GetGameZip?id={sub_match_id}&lng=en"
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


async def collect_fan_sport_league_matches(league_id: int, sport_id: int, mats: dict, match_type: str):
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
                "start_time": datetime.datetime.fromtimestamp(match["S"]),
                "d2by_id": mat_id,
                "sub_matches": [sub[match_key] for sub in match.get("SG", [])]
                if sport_id == 40
                else [],
            }
            for mat_id, mat in mats.items()
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


async def collect_fan_sport_match_data(
    sub_match: int, match_id: int, match_type: str
):
    bets = await get_fan_sport_match_data(sub_match, match_type)

    if bets["Success"]:
        value = bets["Value"]

        n_map = value.get("P", None)

        if bets:
            fan_team_1 = update_team_name(value["O1"])
            fan_team_2 = update_team_name(value["O2"])

            d2by_bets = await get_bets_of_match(match_id, n_map)

            bets = value["E"]

            if d2by_bets:
                is_reverse = is_reversed(
                    d2by_bets[0][6],
                    d2by_bets[0][7],
                    fan_team_1,
                    fan_team_2,
                )
            else:
                return

            cfs = {}
            for d2by_bet in d2by_bets:
                for bet in bets:
                    bet_model = betsModel.get(str(bet["T"]), {})

                    if bet_model["GN"] == d2by_bet[3] or bet_model["GN"] == d2by_bet[4]:
                        if is_reverse:
                            value = bet.get("P", None)
                            if "Handicap" in bet_model["GN"]:
                                b_data = cfs.get(d2by_bet[0], None)

                                if str(d2by_bet[8]) in bet_model["N"] and value == d2by_bet[1]:
                                    team = 1 if d2by_bet[8] == 2 else 2

                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_{team}_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_{team}_win": bet["C"]})
                                elif str(d2by_bet[8]) not in bet_model["N"] and value == -1 * d2by_bet[1]:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_{d2by_bet[8]}_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_{d2by_bet[8]}_win": bet["C"]})
                            elif "Frags, Race To" in bet_model["GN"]:
                                if str(int(value)) in d2by_bet[9]:
                                    b_data = cfs.get(d2by_bet[0], None)
                                    if not b_data:
                                        if "W2" in bet_model["N"]:
                                            cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_1_win": bet["C"]}
                                        else:
                                            cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_2_win": bet["C"]}
                                    else:
                                        if "W2" in bet_model["N"]:
                                            cfs[d2by_bet[0]].update({f"fan_1_win": bet["C"]})
                                        else:
                                            cfs[d2by_bet[0]].update({f"fan_2_win": bet["C"]})
                            elif "Total" in bet_model["GN"] and "Handicap" not in bet_model["GN"]:
                                pass
                            else:
                                b_data = cfs.get(d2by_bet[0], None)
                                if value == d2by_bet[1] and "1" in bet_model["N"]:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_2_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_2_win": bet["C"]})
                                elif value == d2by_bet[1] and "2" in bet_model["N"]:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_1_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_1_win": bet["C"]})
                        else:
                            value = bet.get("P", None)

                            if "Handicap" in bet_model["GN"]:
                                b_data = cfs.get(d2by_bet[0], None)
                                if str(d2by_bet[8]) in bet_model["N"] and value == d2by_bet[1] * -1:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_{d2by_bet[8]}_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_{d2by_bet[8]}_win": bet["C"]})
                                elif value == d2by_bet[1] and str(d2by_bet[8]) not in bet_model["N"]:
                                    team = 1 if d2by_bet[8] == 2 else 2

                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_{team}_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_{team}_win": bet["C"]})
                            elif "Frags, Race To" in bet_model["GN"]:
                                if str(int(value)) in d2by_bet[9]:
                                    b_data = cfs.get(d2by_bet[0], None)
                                    if not b_data:
                                        if "W2" in bet_model["N"]:
                                            cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_2_win": bet["C"]}
                                        else:
                                            cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_1_win": bet["C"]}
                                    else:
                                        if "W2" in bet_model["N"]:
                                            cfs[d2by_bet[0]].update({f"fan_2_win": bet["C"]})
                                        else:
                                            cfs[d2by_bet[0]].update({f"fan_1_win": bet["C"]})
                            elif "Total" in bet_model["GN"] and "Handicap" not in bet_model["GN"]:
                                pass
                            else:
                                b_data = cfs.get(d2by_bet[0], None)
                                if value == d2by_bet[1] and "1" in bet_model["N"]:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_1_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_1_win": bet["C"]})
                                elif value == d2by_bet[1] and "2" in bet_model["N"]:
                                    if not b_data:
                                        cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_2_win": bet["C"]}
                                    else:
                                        cfs[d2by_bet[0]].update({f"fan_2_win": bet["C"]})

                        if "Total" in bet_model["GN"] and "Handicap" not in bet_model["GN"]:
                            value = bet.get("P", None)

                            b_data = cfs.get(d2by_bet[0], None)
                            if "Over" in bet_model["N"] and value == d2by_bet[1]:
                                if not b_data:
                                    cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_1_win": bet["C"]}
                                else:
                                    cfs[d2by_bet[0]].update({f"fan_1_win": bet["C"]})
                            elif "Under" in bet_model["N"] and value == d2by_bet[1]:
                                if not b_data:
                                    cfs[d2by_bet[0]] = {"id": d2by_bet[0], f"fan_2_win": bet["C"]}
                                else:
                                    cfs[d2by_bet[0]].update({f"fan_2_win": bet["C"]})

            tasks = [update_bet(cf) for cf in cfs.values()]
            await asyncio.gather(*tasks)
    else:
        return []
