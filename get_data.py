import asyncio
import copy
import datetime
import json
import aiohttp
import logging

from betsModel import betsModel
from database.functions import (
    add_match_to_db,
    add_bet_type,
    add_bet,
    get_bets_of_match,
    update_bet,
)
from database.tables import d2by_matches, fan_sport_matches


async def get_d2by_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.d2by.com/api/v1/web/matchs?isFinish=false&isCancel=false&pageSize=1000"
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)

    if matches["meta"]["status"] == 200:
        matches = matches["data"]["resultData"]

        leagues = {}
        res_matches = {}
        for match in matches:
            game = match["game"]["title"]
            lg = match["tournament"]["title"].split(" ")[0]

            gm = leagues.get(game)
            if gm:
                gm.add(lg.lower())
            else:
                leagues[game] = set()
                leagues[game].add(lg.lower())

            team_1 = match["teamA"]["title"].strip().lower()
            team_2 = match["teamB"]["title"].strip().lower()
            start_time = datetime.datetime.strptime(
                match["minStartTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) + datetime.timedelta(hours=1)

            data = {
                "team_1": team_1,
                "team_2": team_2,
                "start_time": start_time,
                "game": game,
                "league": lg,
            }
            match_id = await add_match_to_db(data, d2by_matches)

            res_matches[match_id] = {
                "teams": (team_1, team_2),
                "start_time": start_time,
                "game": game,
            }

            for bet in match["betType"]:
                bet_data = {
                    "type": bet["betTypeConfig"]["type"],
                    "order": bet["betTypeConfig"]["order"]
                    if not isinstance(bet["betTypeConfig"]["order"], dict)
                    else 0,
                    "description": bet["betTypeConfig"]["title"],
                }
                bet_type_id = await add_bet_type(bet_data)

                if bet["rateTeamA"] != 1 and bet["rateTeamB"] != 1:
                    above_bets = bet["aboveBets"]
                    if above_bets == "A":
                        above_bets = 1
                    elif above_bets == "B":
                        above_bets = 2
                    else:
                        above_bets = None

                    bet_data = {
                        "isActive": bet["isActive"],
                        "values": bet["values"],
                        "d2by_1_win": bet["rateTeamA"],
                        "d2by_2_win": bet["rateTeamB"],
                        "match_id": match_id,
                        "type_id": bet_type_id,
                        "above_bets": above_bets,
                        "start_time": datetime.datetime.strptime(
                            bet["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
                        )
                        + datetime.timedelta(hours=1),
                    }
                    await add_bet(bet_data)
        return leagues, res_matches
    else:
        logging.error("d2by not success")
        return {}, {}


async def get_fan_sport_leagues(sport: int, lgs: set = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/LineFeed/GetChampsZip?sport={sport}&lng=en"
        ) as resp:
            response = await resp.text()
            leagues = json.loads(response)
    if leagues["Success"]:
        leagues = leagues["Value"]

        if lgs:
            res = []
            for league in leagues:
                for lg in lgs:
                    if lg in league["L"].lower():
                        res.append(league["LI"])
        else:
            res = [league["LI"] for league in leagues]

        logging.error(f"leagues: {res}")
        return res
    else:
        logging.error("get_fan_sport_leagues not success")
        return []


def remove_id_key(d):
    d.pop("id", None)
    d.pop("sub_matches", None)
    return d


async def get_fan_sport_league_matches(league_id: int, sport_id: int, mats: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/LineFeed/GetChampZip?lng=en&champ={league_id}"
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)
    if matches["Success"]:
        matches = matches["Value"]["G"]

        logging.error(f"matches: {matches}")
        res = [
            {
                "id": match["CI"],
                "team_1": match["O1"].lower(),
                "team_2": match["O2"].lower(),
                "start_time": datetime.datetime.fromtimestamp(match["S"]),
                "d2by_id": mat_id,
                "sub_matches": [sub["CI"] for sub in match("SG", None)]
                if sport_id == 40
                else [],
            }
            for mat_id, mat in mats.items()
            for match in matches
            if (
                match["O1"].lower() in mat["teams"]
                or match["O2"].lower() in mat["teams"]
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
        logging.error("get_fan_sport_league_matches not success")
        return []


async def get_fan_sport_match_data(
    sub_match_id: str, match_id: int, fan_team_1: str, fan_team_2: str
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://fan-sport.com/LineFeed/GetGameZip?id={sub_match_id}"
        ) as resp:
            response = await resp.text()
            bets = json.loads(response)
    if bets["Success"]:
        value = bets["Value"]

        n_map = value.get("P", None)

        if bets:
            d2by_bets = await get_bets_of_match(match_id, n_map)

            bets = value["E"]

            cfs = {}
            for d2by_bet in d2by_bets:
                for bet in bets:
                    bet_model = betsModel.get(str(bet["T"]), {})
                    if "Handicap" in bet_model["GN"] and (
                        bet_model["GN"] == d2by_bet[3] or bet_model["GN"] == d2by_bet[4]
                    ):
                        if (
                            bet.get("P", None) == -1 * d2by_bet[1]
                            and str(d2by_bet[8]) in bet_model["N"]
                        ) or (
                            bet.get("P", None) == d2by_bet[1]
                            and str(d2by_bet[8]) not in bet_model["N"]
                        ):
                            b_data = cfs.get(d2by_bet[0], None)
                            if b_data is None:
                                cfs[d2by_bet[0]] = (bet["C"],)
                            else:
                                cfs[d2by_bet[0]] += (bet["C"],)
                    elif bet.get("P", None) == d2by_bet[1] and (
                        bet_model["GN"] == d2by_bet[3] or bet_model["GN"] == d2by_bet[4]
                    ):
                        b_data = cfs.get(d2by_bet[0], None)
                        if b_data is None:
                            cfs[d2by_bet[0]] = (bet["C"],)
                        else:
                            cfs[d2by_bet[0]] += (bet["C"],)

                if fan_team_1 == d2by_bet[7] or fan_team_2 == d2by_bet[6]:
                    cfs[d2by_bet[0]] = (cfs[d2by_bet[0]][1], cfs[d2by_bet[0]][0])

            logging.error(f"cfs: {cfs}")
            for bet, cf in cfs.items():
                try:
                    await update_bet(
                        {"id": bet, "fan_1_win": cf[0], "fan_2_win": cf[1]}
                    )
                except:
                    pass
    else:
        logging.error("get_fan_sport_league_matches not success")
        return []