import datetime

from config import AUTH_TOKEN
from roulette.api import (
    get_current_roulette,
    calculate_bets_for_roulette,
    make_bet_on_roulette,
)


async def roulette():
    while True:
        main_bet = None
        zero_bet = None

        roulette_id, finish, status = await get_current_roulette(AUTH_TOKEN)

        finish = datetime.datetime.strptime(finish, "%Y-%m-%dT%H:%M:%S.%fZ")

        is_bet = True
        while is_bet:
            now = datetime.datetime.utcnow()

            if finish - now < datetime.timedelta(seconds=3) and status == "BETTING":
                if main_bet:
                    await make_bet_on_roulette(AUTH_TOKEN, roulette_id, main_bet)
                    print("Made bet: ", main_bet["amount"], "at: ", now)
                if zero_bet:
                    await make_bet_on_roulette(AUTH_TOKEN, roulette_id, main_bet)

                is_bet = False
            elif status == "COMPLETED":
                is_bet = False
            else:
                main_bet, zero_bet = await calculate_bets_for_roulette(AUTH_TOKEN, roulette_id)
