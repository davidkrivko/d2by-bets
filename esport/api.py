import asyncio
import datetime
import json
import aiohttp

from config import D2BY_TIME_DELTA, DEFAULT_D2BY_HEADERS
from database.v2.bets import (
    add_bet_type,
    add_bet,
)
from database.v2.matches import add_match_to_db

from database.v2.tables import d2by_matches
from utils import update_team_name


async def collect_d2by_v2_matches():
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://api.d2by.com/api/v2/web/matchs?pageSize=1000&sort=scheduledAt&status=pre_match,live",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

    data = response["data"]["datas"]

    matches = [
        dict(
            d2by_id=match["id"],
            team_1=update_team_name(match["opponents"][0]["name"]),
            team_2=update_team_name(match["opponents"][1]["name"]),
            team_1_short=match["opponents"][0]["acronym"]
            if match["opponents"][0]["acronym"]
            else match["opponents"][0]["name"],
            team_2_short=match["opponents"][1]["acronym"]
            if match["opponents"][1]["acronym"]
            else match["opponents"][1]["name"],
            d2by_url=f"https://d2by.com/esports/{match['slug']}",
            start_time=datetime.datetime.strptime(
                match["beginAt"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            + datetime.timedelta(hours=D2BY_TIME_DELTA),
            game=match["videogame"]["name"],
        )
        for match in data
        if not match.get("endAt")
    ]

    tasks = [add_match_to_db(match, d2by_matches) for match in matches]
    mats = await asyncio.gather(*tasks)

    return mats


async def get_bets_of_d2by_match(match: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.d2by.com/api/v2/web/matchs/{match['d2by_id']}/markets",
            ssl=False
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
    bet_type = await add_bet_type(bet_type_data)

    selections = bet_data["selections"]

    if bet_type and selections:
        bet = dict(
            map_v2=bet_data["gamePosition"],
            isActive=True if bet_data["status"] == "active" else False,
            type_id=bet_type["id"],
            match_id=match["id"],
            bet_id=bet_data["id"],
            d2by_bets={},
            d2by_probs={},
        )

        for selection in selections:
            prob = (
                1
                if selection["probability_with_margin"] == 0
                else selection["probability_with_margin"]
            )
            prob = (
                1
                if prob is None
                else prob
            )
            cf = round(1 / prob, 3)
            if "correct-score" == bet_data["template"]:
                bet["d2by_bets"].update(
                    {f"{selection['score_home']}-{selection['score_away']}": cf}
                )
                bet["d2by_probs"].update(
                    {
                        f"{selection['score_home']}-{selection['score_away']}": {
                            "prob": prob,
                            "position": selection["position"],
                        }
                    }
                )
            else:
                if selection["name"] == match["team_1_short"]:
                    team = "1"
                elif selection["name"] == match["team_2_short"]:
                    team = "2"
                else:
                    team = selection["name"]
                bet["d2by_bets"].update({team: cf})
                bet["d2by_probs"].update(
                    {team: {"prob": prob, "position": selection["position"]}}
                )

        if "handicap" in bet_data["template"]:
            bet["above_bets"] = 1 if selections[0]["handicap"] < 0 else 2
            bet["value"] = abs(selections[0]["handicap"])

        if "over-under" in bet_data["template"]:
            bet["value"] = float(bet_data["line"])
        elif (
            "-n-" in bet_data["template"] or "round-first-to-n" == bet_data["template"]
        ):
            bet["value"] = float(bet_data["line"])
        elif "player-kill-to-get-n" == bet_data["template"]:
            bet["above_bets"] = 1 if bet_data["participantSide"] == "home" else 2
            bet["value"] = int(bet_data["line"])
        elif "player-kill-over-under" == bet_data["template"]:
            bet["extra"] = bet_data["name"].split()[0]

        if "participant" in bet_data["template"]:
            bet["above_bets"] = 1 if bet_data["participantSide"] == "home" else 2

        await add_bet(bet)


async def make_bet(auth_token, data):
    headers = DEFAULT_D2BY_HEADERS
    headers["authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            "https://api.d2by.com/api/v2/web/matchs/predicts", json=[data],
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            if response["meta"]["status"] == 200:
                return {"status": "Success", "market": data["market"]}
            else:
                return {"status": response["meta"]["internalMessage"], "market": data["market"]}
