import asyncio

from config import IS_ALL_MATCHES
from database.v2.bets import get_all_active_bets, is_shown_update, get_bet_from_market
from database.v2.matches import (
    get_d2by_live_matches,
    get_d2by_line_matches,
    get_fan_sport_live_matches,
    get_fan_sport_line_matches,
)

from esport.fan_sport import compare_bets_v2
from esport.api import get_bets_of_d2by_match, make_bet
from telegram import send_match_to_telegram_v2


def query_compare_bet_cfs_v2(d2by_bets, fan_bets):
    for key in d2by_bets:
        if key in fan_bets:
            value1 = d2by_bets[key]
            value2 = fan_bets[key]

            if value1 / value2 >= 1.15:
                return key

    return False


async def v2_script(time: str, token):
    if time == "LiveFeed":
        matches = await get_d2by_live_matches()
        mats = await get_fan_sport_live_matches()
    else:
        matches = await get_d2by_line_matches(is_all=IS_ALL_MATCHES)
        mats = await get_fan_sport_line_matches(is_all=IS_ALL_MATCHES)

    tasks = [get_bets_of_d2by_match(match) for match in matches]
    await asyncio.gather(*tasks)

    tasks = []
    for mat in mats:
        tasks.extend([
            compare_bets_v2(sub_mat, mat["d2by_id"], time, 40)
            for sub_mat in mat["fan_ids"].split(",")
        ])

    await asyncio.gather(*tasks)

    all_bets = await get_all_active_bets()

    bets = []
    tasks = []
    for bet in all_bets:
        if bet[16] is False:
            key = query_compare_bet_cfs_v2(bet[1], bet[2])
            if key:
                prob = bet[15][key]

                if prob["prob"] > 0.28:
                    bets.append(list(bet))

                    data = {
                        "amount": 1,
                        "coinType": "GEM",
                        "market": bet[14],
                        "type": "SINGLE",
                        "currentRate": prob["prob"],
                        "selectPosition": prob["position"],
                    }
                    tasks.append(make_bet(token, data))

    responses = await asyncio.gather(*tasks)

    tasks = [get_bet_from_market(data) for data in responses]
    bets = await asyncio.gather(*tasks)

    success_bets = [bet[0] for bet in bets]
    await is_shown_update(success_bets)

    await asyncio.gather(*[send_match_to_telegram_v2(bets_data) for bets_data in bets if bets_data[16] is False])
