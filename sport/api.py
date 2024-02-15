import datetime
import json
import re

import aiohttp

from config import D2BY_TIME_DELTA, DEFAULT_D2BY_HEADERS
from database.v1.bets import (
    add_bet_type,
    add_bet,
)
from database.v1.matches import add_match_to_db

from database.v1.tables import d2by_matches
from utils import update_team_name, create_new_token


async def collect_d2by_sport_matches():
    async with aiohttp.ClientSession(headers=DEFAULT_D2BY_HEADERS) as session:
        async with session.get(
            "https://api.d2by.com/api/v1/web/matchs?isFinish=false&isCancel=false&pageSize=1000"
        ) as resp:
            response = await resp.text()
            matches = json.loads(response)
    if matches["meta"]["status"] == 200:
        if not matches.get("data"):
            return {}, {}

        matches = matches["data"]["resultData"]

        leagues = {}
        res_matches = {}
        for match in matches:
            game = match["game"]["title"]
            lg = match["tournament"]["title"].split(" ")[0].lower()

            lg = re.sub(r'[^a-z]', '', lg)

            gm = leagues.get(game)
            if gm:
                gm.add(lg)
            else:
                leagues[game] = set()
                leagues[game].add(lg)

            team_1 = update_team_name(match["teamA"]["title"])
            team_2 = update_team_name(match["teamB"]["title"])

            if team_1 == "bb":
                team_1 = "betboom"
            if team_2 == "bb":
                team_2 = "betboom"

            start_time = datetime.datetime.strptime(
                match["minStartTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) + datetime.timedelta(hours=D2BY_TIME_DELTA)
            if match["match"]["isActive"]:
                data = {
                    "team_1": team_1,
                    "team_2": team_2,
                    "start_time": start_time,
                    "game": game,
                    "league": lg,
                }
                full_match = await add_match_to_db(data, d2by_matches)

                res_matches[full_match["id"]] = {
                    "team_1": team_1,
                    "team_2": team_2,
                    "teams": (team_1, team_2),
                    "start_time": start_time,
                    "game": game,
                }

                for bet in match["betType"]:
                    bet_data = {
                        "type": bet["betTypeConfig"]["type"],
                        "description": bet["betTypeConfig"]["title"],
                    }
                    bet_type = await add_bet_type(bet_data)

                    if bet["rateTeamA"] != 1 and bet["rateTeamB"] != 1:
                        above_bets = bet["aboveBets"]
                        if above_bets == "A":
                            above_bets = 1
                        elif above_bets == "B":
                            above_bets = 2
                        else:
                            above_bets = None

                        if (
                            bet["isLive"]
                            or bet["isFinish"]
                            or bet["isCancel"]
                            or bet["isDeleted"]
                        ):
                            is_active = False
                        else:
                            is_active = True

                        bet_data = {
                            "isActive": is_active,
                            "value": bet["values"],
                            "d2by_1_win": bet["rateTeamA"],
                            "d2by_2_win": bet["rateTeamB"],
                            "match_id": full_match["id"],
                            "type_id": bet_type["id"],
                            "above_bets": above_bets,
                            "amount_1_win": bet["totalAmountTeamA"],
                            "amount_2_win": bet["totalAmountTeamB"],
                            "start_time": datetime.datetime.strptime(
                                bet["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ"
                            )
                            + datetime.timedelta(hours=D2BY_TIME_DELTA),
                            "d2by_url": f"https://d2by.com/match/{match['match']['shortId']}-{bet['shortId']}",
                            "fan_url": f"",
                        }
                        await add_bet(bet_data)
        return leagues, res_matches
    else:
        return {}, {}


async def make_bet(auth_token, data):
    headers = DEFAULT_D2BY_HEADERS
    headers["Authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            "https://api.d2by.com/api/v1/web/bets/bet", json=data
        ) as resp:
            if resp.status != 200:
                token = await create_new_token(auth_token)
                await make_bet(token, data)
            else:
                response = await resp.text()
                response = json.loads(response)

    return response
