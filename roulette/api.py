import json

import aiohttp
import pandas as pd


async def get_current_roulette(auth_token):
    async with aiohttp.ClientSession(cookies=[auth_token]) as session:
        async with session.get("https://api.d2by.com/api/v1/web/game-x2/now") as resp:
            response = await resp.text()
            data = json.loads(response)

    if data["meta"]["status"] == 200:
        data = data["data"]
        return data["id"], data["completedAt"], data["status"]


async def calculate_bets_for_roulette(auth_token, roulette_id):
    async with aiohttp.ClientSession(cookies=[auth_token]) as session:
        async with session.get(
            f"https://api.d2by.com/api/v1/web/game-x2/{roulette_id}/predicts"
        ) as resp:
            response = await resp.text()
            data = json.loads(response)

    if data["meta"]["status"] == 200:
        data = data["data"]
        if data:
            df = pd.DataFrame(data)

            # Group by 'colorPredict' and sum 'amount'
            amounts = df.groupby("colorPredict")["amount"].sum()

            # If you want to ensure that all colors are represented, even if they are not in the data:
            colors = ["GREEN", "RED", "BLACK"]
            amounts = amounts.reindex(colors, fill_value=0)

            # Convert to dictionary if needed
            amounts_dict = amounts.to_dict()

            diff = amounts_dict["BLACK"] - amounts_dict["RED"]

            main_bet_data = {}
            zero_bet_data = {}

            zero_sum = sum((amounts_dict["BLACK"], amounts_dict["RED"])) / 15
            zero_sum = round(zero_sum, 3) - amounts_dict["GREEN"]
            if zero_sum > 0.01:
                if (amounts_dict["BLACK"] and amounts_dict["RED"]) or (amounts_dict["BLACK"] > 0.15 or amounts_dict["RED"] > 0.15):
                    zero_bet_data = {
                        "coinType": "GOLD",
                        "colorPredict": "GREEN",
                        "amount": zero_sum,
                    }
            elif 0.03 < amounts_dict["BLACK"] < 0.1 or 0.03 < amounts_dict["RED"] < 0.1 and amounts_dict["GREEN"] == 0:
                zero_bet_data = {
                    "coinType": "GOLD",
                    "colorPredict": "GREEN",
                    "amount": 0.01,
                }
                zero_sum = 0.01
            else:
                zero_sum = 0

            if diff > 0:
                bet = diff - 0.02 - zero_sum
                if bet > 0.01:
                    main_bet_data = {"coinType": "GOLD", "colorPredict": "RED", "amount": round(bet, 3)}
            elif diff < 0:
                bet = abs(diff) - 0.02 - zero_sum
                if bet > 0.01:
                    main_bet_data = {"coinType": "GOLD", "colorPredict": "BLACK", "amount": round(bet, 3)}

            return main_bet_data, zero_bet_data

        return {}, {}


async def make_bet_on_roulette(auth_token, roulette_id, data):
    headers = {"Authorization": f"Bearer {auth_token['value']}"}

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.post(
            f"https://api.d2by.com/api/v1/web/game-x2/{roulette_id}/predicts", json=data
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            return response
