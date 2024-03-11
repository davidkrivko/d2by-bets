import json

import aiohttp

from login.api import create_new_token


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