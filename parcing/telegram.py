import datetime
import aiohttp

from config import TELEGRAM_BOT, CHAT_ID
from database.functions.matches import update_is_shown_field


async def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}

    async with aiohttp.ClientSession() as session:
        async with session.post(telegram_url, data=data) as response:
            t = await response.text()
            return t


def escape_markdown_v2(string):
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in string)


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
def bet_message(bet):
    if 'Handicap' in bet[7]:
        sub_str = "negative "
        if bet[15] is not None and bet[15] == '1':
            sub_str += f"{bet[5]} for team {bet[9]}"
        else:
            sub_str += f"{bet[5]} for team {bet[10]}"
    else:
        sub_str = f"{bet[5]}"

    message = (
        f"       **{bet[11]}**    \n"
        f"**{bet[9]} \\- {bet[10]}**\n"
        f"**{bet[7]}:** {sub_str}\n"
        f"__D2BY__: **{bet[1]}** \\- **{bet[2]}**\n"
        f"__FanSport__: {bet[3]} \\- {bet[4]}\n"
        f"Bet active until {bet[6]}\n"
    )
    return message


async def send_bets_to_telegram(bets_data: list):
    now = datetime.datetime.now() + datetime.timedelta(hours=1)
    for bet in bets_data:
        if bet[6] > now:
            diff = bet[6] - now

            if diff < datetime.timedelta(minutes=2) and bet[12] is False:
                await update_is_shown_field(bet[0], {"is_shown_2": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]
                message = bet_message(bet)
                await send_telegram_message(message)
            elif diff < datetime.timedelta(minutes=5) and bet[13] is False:
                await update_is_shown_field(bet[0], {"is_shown_5": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]
                message = bet_message(bet)
                await send_telegram_message(message)
            elif diff < datetime.timedelta(minutes=10) and bet[14] is False:
                await update_is_shown_field(bet[0], {"is_shown_10": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]
                message = bet_message(bet)
                await send_telegram_message(message)
