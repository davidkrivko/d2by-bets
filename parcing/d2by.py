import asyncio
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
from database.tables import bets_type as bets_type_table, bets_type_v2 as bets_type_v2_table
from parcing.utils import update_team_name, create_new_token


async def get_d2by_sport_matches():
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
                    bet_type = await add_bet_type(bet_data, bets_type_table)

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
                            "values": bet["values"],
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


async def get_trade_items(auth_token):
    headers = {"Authorization": f"Bearer {auth_token['value']}"}

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.get(
            "https://api.d2by.com/api/v1/web/inventories"
            "?pageSize=10000&type=DOTA2&page=1&sort=-item.price&isTradable=true"
        ) as resp:
            if resp.status != 200:
                token = await create_new_token()

                await get_trade_items(token)
            else:
                response = await resp.text()
                response = json.loads(response)

    items = response["data"]["datas"]

    for item in items:
        print(item)


async def make_bet(auth_token, data):
    headers = {"Authorization": f"Bearer {auth_token['value']}"}

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            "https://api.d2by.com/api/v1/web/bets/bet", data=data
        ) as resp:
            if resp.status != 200:
                token = await create_new_token()
                await get_trade_items(token)
            else:
                response = await resp.text()
                response = json.loads(response)

    return response


async def get_d2by_cybersport_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.d2by.com/api/v2/web/matchs?pageSize=1000&sort=scheduledAt&status=pre_match,live"
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]["datas"]

    matches = [
        dict(
            d2by_id=match["id"],
            team_1=update_team_name(match["opponents"][0]["name"]),
            team_2=update_team_name(match["opponents"][1]["name"]),
            team_1_short=match["opponents"][0]["acronym"],
            team_2_short=match["opponents"][1]["acronym"],
            start_time=datetime.datetime.strptime(
                match["beginAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            + datetime.timedelta(hours=D2BY_TIME_DELTA),
            game=match["videogame"]["name"],
        )
        for match in data
    ]

    tasks = [add_match_to_db(match, d2by_matches) for match in matches]
    mats = await asyncio.gather(*tasks)

    return mats


async def get_bets_of_d2by_match(match: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.d2by.com/api/v2/web/matchs/{match['d2by_id']}/markets"
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]

    tasks = [create_bet_v2(bet, match) for bet in data]
    await asyncio.gather(*tasks)


async def create_bet_v2(bet_data: dict, match: dict):
    bet_type_data = {
        "description": bet_data["name"],
        "type": bet_data["template"],
    }
    bet_type = await add_bet_type(bet_type_data, bets_type_v2_table)

    if bet_type and "correct-score" != bet_type["type"]:
        team_1 = bet_data["selections"][0]["probability_with_margin"]
        team_2 = bet_data["selections"][1]["probability_with_margin"]
        if team_1 and team_2:
            bet = dict(
                d2by_1_win=1 / team_1,
                d2by_2_win=1 / team_2,
                map_v2=bet_data["gamePosition"],
                isActive=True if bet_data["status"] == "active" else False,
                type_id=bet_type["id"],
                match_id=match["id"],
                values=None,
                extra=None,
            )

            if "3-way" in bet_type["type"]:
                bet["d2by_draw"] = 1 / bet_data["selections"][1]["probability_with_margin"]
                bet["d2by_2_win"] = 1 / bet_data["selections"][2]["probability_with_margin"]

            if "handicap" in bet_type["type"]:
                bet["above_bets"] = 1 if bet_data["selections"][0]["handicap"] < 0 else 2
                bet["values"] = abs(bet_data["selections"][0]["handicap"])

            if "over-under" in bet_type["type"]:
                bet["values"] = float(bet_data["line"])
            elif "-n-" in bet_type["type"]:
                bet["values"] = float(bet_data["line"])

            await add_bet(bet)
