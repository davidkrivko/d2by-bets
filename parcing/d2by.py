import datetime
import json
import aiohttp

from config import D2BY_TIME_DELTA
from database.functions.bets import (
    add_bet_type,
    add_bet,
)
from database.functions.matches import add_match_to_db

from database.tables import d2by_matches
from login.api import get_token
from parcing.utils import update_team_name


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
                match_id = await add_match_to_db(data, d2by_matches)

                res_matches[match_id] = {
                    "team_1": team_1,
                    "team_2": team_2,
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

                        if bet["isLive"] or bet["isFinish"] or bet["isCancel"] or bet["isDeleted"]:
                            is_active = False
                        else:
                            is_active = True

                        bet_data = {
                            "isActive": is_active,
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
        return {}, {}
