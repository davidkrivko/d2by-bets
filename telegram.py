import datetime
import aiohttp

from config import TELEGRAM_BOT, CHAT_ID, SENDING_MESSAGES_DELTA
from database.v1.bets import update_is_shown_field
from sport.api import make_bet


async def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}

    async with aiohttp.ClientSession() as session:
        async with session.post(telegram_url, data=data) as response:
            t = await response.text()
            return t


def escape_markdown_v2(string):
    if "https" not in string:
        escape_chars = "_*[]()~`>#+-=|{}.!"
        for char in escape_chars:
            string = string.replace(char, f"\\{char}")
    return string


# 1. id,
# 2. d2by_1_win,
# 3. d2by_2_win,
# 4. fan_1_win,
# 5. fan_2_win,
# 6. "values"
# 7. start_time,
# 8. description,
# 9. id.label("match_id"),
# 10. team_1,
# 11. team_2,
# 12. game,
# 13. is_shown_2,
# 14. is_shown_5,
# 15. is_shown_10,
# 16. above_bets,
# 17. bets.c.amount_1_win,
# 18. bets.c.amount_2_win,
# 19. bets.c.d2by_url,
# 20.  bets.c.fan_url,
def bet_message(bet):
    if "Handicap" in bet[7]:
        sub_str = "negative "
        if bet[15] is not None and bet[15] == "1":
            sub_str += f"{bet[5]} for team {bet[9]}"
        else:
            sub_str += f"{bet[5]} for team {bet[10]}"
    else:
        sub_str = f"{bet[5]}"

    message = (
        f"       **{bet[11]}**    \n"
        f"**{bet[9]} \\- {bet[10]}**\n"
        f"**{bet[7]}:** {sub_str}\n"
        f"[D2BY]({bet[18]}): **{bet[1]} \\({bet[16]} $\\)**\\- **{bet[2]} \\({bet[17]} $\\)**\n"
        f"[FanSport]({bet[19]}): {bet[3]} \\- {bet[4]}\n"
        f"Bet active until {bet[6]}\n"
    )
    return message


async def send_bets_to_telegram(bets_data: list):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=SENDING_MESSAGES_DELTA)
    for bet in bets_data:
        if bet[6] > now:
            diff = bet[6] - now

            if diff < datetime.timedelta(minutes=2) and bet[12] is False:
                # await make_bet()

                await update_is_shown_field(bet[0], {"is_shown_2": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]
                message = bet_message(bet)
                await send_telegram_message(message)


# bet_table.c.id, 0
# bet_table.c.d2by_bets, 1
# bet_table.c.fan_bets, 2
# bet_table.c["value"].label("bet_values"), 3
# bet_table.c.start_time, 4
# bet_type_table.c.description, 5
# d2by_matches.c.id.label("match_id"), 6
# d2by_matches.c.team_1, 7
# d2by_matches.c.team_2, 8
# d2by_matches.c.game, 9
# bet_table.c.above_bets, 10
# d2by_matches.c.d2by_url, 11
# bet_table.c.fan_url, 12
# bets_table.c.map_v2, 13
# bets_table.c.bet_id 14
# bets_table.c.is_shown 15
# bet_table.c.d2by_probs, 16
# bet status 17
async def send_match_to_telegram_v2(bets_data: list):
    fan_bets = bets_data[2]
    fan_bets = "".join([f"{key} : {value} - " for key, value in fan_bets.items()])

    d2by_bets = bets_data[1]
    d2by_bets = "".join([f"{key} : {value} - " for key, value in d2by_bets.items()])

    bets_data[1] = d2by_bets
    bets_data[2] = fan_bets

    bet = [escape_markdown_v2(str(i)) for i in bets_data]

    if "Handicap" in bet[5]:
        sub_str = "negative "
        if bet[10] is not None and bet[10] == "1":
            sub_str += f"{bet[3]} for team {bet[7]}"
        else:
            sub_str += f"{bet[3]} for team {bet[8]}"
    else:
        sub_str = f"{bet[3]}"

    message = (
        f"       **{bet[9]}**    \n"
        f"**{bet[7]} \\- {bet[8]}**\n"
        f"**{bet[5]} {bet[13]}:** {sub_str}\n"
        f"[D2BY]({bet[11]}): **{bet[1]}**\n"
        f"[FanSport]({bet[12]}): **{bet[2]}**\n"
        f"Bet status: **{bet[17]}**\n"
    )
    await send_telegram_message(message)

    return int(bet[0])
