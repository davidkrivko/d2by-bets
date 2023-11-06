import datetime
import os

import aiohttp
from sqlalchemy import Table, text, func
from sqlalchemy.sql import select
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.connection import async_session, db, meta
from database.tables import fan_sport_matches, d2by_matches, bets_type, bets

TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT")
CHAT_ID = os.environ.get("CHAT_ID")


async def send_telegram_message(message):
    telegram_url = f"https://api.telegram.org/{TELEGRAM_BOT}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}

    async with aiohttp.ClientSession() as session:
        async with session.post(telegram_url, data=data) as response:
            t = await response.text()
            return t


async def update_match_active(data, match):
    if data["start_time"] != match[3]:
        async with async_session() as session:
            update_stmt = (
                d2by_matches.update().where(d2by_matches.c.id == match[0]).values(data)
            )

            try:
                await session.execute(update_stmt)
                await session.commit()
            except SQLTimeoutError:
                return match[0]
            except:
                return match[0]


async def add_match_to_db(data: dict, table: Table):
    teams = (data["team_1"], data["team_2"])

    async with async_session() as session:
        match_statement = (
            table.select()
            .where(
                ((table.c.team_1.in_(teams)) | (table.c.team_2.in_(teams)))
                & (
                    table.c.start_time.between(
                        data["start_time"] - datetime.timedelta(minutes=10),
                        data["start_time"] + datetime.timedelta(minutes=10),
                    )
                )
            )
            .limit(1)
        )
        try:
            result_set = await session.execute(match_statement)
            match = result_set.fetchone()

            if table is d2by_matches:
                await update_match_active(data, match)

            return match[0]
        except SQLTimeoutError:
            return
        except:
            match = None

    if match is None:
        async with async_session() as session:
            insert_stmt = table.insert().values(
                data,
            )
            try:
                res = await session.execute(insert_stmt)
                await session.commit()

                return res.inserted_primary_key[0]
            except SQLTimeoutError:
                return


async def update_is_shown_field(bet_id: int, data: dict):
    async with async_session() as session:
        update_stmt = bets.update().where(bets.c.id == bet_id).values(data)
        try:
            await session.execute(update_stmt)
            await session.commit()
        except SQLTimeoutError:
            return
        except:
            return


# async def get_same_matches_matches():
#     matches = []
#     async with async_session() as session:
#         join_statement = d2by_matches.join(
#             fan_sport_matches,
#             (fan_sport_matches.c.team_1 == d2by_matches.c.team_1)
#             & fan_sport_matches.c.start_time.between(
#                 d2by_matches.c.start_time - text("interval '10 minute'"),
#                 d2by_matches.c.start_time + text("interval '10 minute'"),
#             )
#             | (
#                 (fan_sport_matches.c.team_2 == d2by_matches.c.team_2)
#                 & fan_sport_matches.c.start_time.between(
#                     d2by_matches.c.start_time - text("interval '10 minute'"),
#                     d2by_matches.c.start_time + text("interval '10 minute'"),
#                 )
#             ),
#         )
#
#         fields = [
#             d2by_matches.c.team_1,
#             d2by_matches.c.team_2,
#             d2by_matches.c.win_1.label("d2by_win_1"),
#             d2by_matches.c.win_2.label("d2by_win_2"),
#             d2by_matches.c.start_time,
#             d2by_matches.c.game,
#             fan_sport_matches.c.win_1.label("fan_win_1"),
#             fan_sport_matches.c.win_2.label("fan_win_2"),
#             d2by_matches.c.is_shown_10,
#             d2by_matches.c.is_shown_5,
#             d2by_matches.c.is_shown_2,
#             d2by_matches.c.id,
#         ]
#
#         query = (
#             d2by_matches.select()
#             .select_from(join_statement)
#             .with_only_columns(*fields)
#             .distinct()
#         )
#         try:
#             result_set = await session.execute(query)
#             matches.extend(result_set.fetchall())
#         except:
#             pass
#
#         join_statement_2 = d2by_matches.join(
#             fan_sport_matches,
#             (
#                 (fan_sport_matches.c.team_1 == d2by_matches.c.team_2)
#                 & fan_sport_matches.c.start_time.between(
#                     d2by_matches.c.start_time - text("interval '10 minute'"),
#                     d2by_matches.c.start_time + text("interval '10 minute'"),
#                 )
#             ) | (
#                 (fan_sport_matches.c.team_2 == d2by_matches.c.team_1)
#                 & fan_sport_matches.c.start_time.between(
#                     d2by_matches.c.start_time - text("interval '10 minute'"),
#                     d2by_matches.c.start_time + text("interval '10 minute'"),
#                 )
#             )
#         )
#
#         fields = [
#             d2by_matches.c.team_1,
#             d2by_matches.c.team_2,
#             d2by_matches.c.win_1.label("d2by_win_1"),
#             d2by_matches.c.win_2.label("d2by_win_2"),
#             d2by_matches.c.start_time,
#             d2by_matches.c.game,
#             fan_sport_matches.c.win_2.label("fan_win_2"),
#             fan_sport_matches.c.win_1.label("fan_win_1"),
#             d2by_matches.c.is_shown_10,
#             d2by_matches.c.is_shown_5,
#             d2by_matches.c.is_shown_2,
#             d2by_matches.c.id,
#         ]
#
#         query = (
#             d2by_matches.select()
#             .select_from(join_statement_2)
#             .with_only_columns(*fields)
#             .distinct()
#         )
#         try:
#             result_set = await session.execute(query)
#             matches.extend(result_set.fetchall())
#         except SQLTimeoutError:
#             return
#         except:
#             pass
#
#         return matches


# async def compare_coef_on_matches(matches):
#     now = datetime.datetime.now()
#     for match in matches:
#         win_1 = round(match[2] / match[6], 2)
#         win_2 = round(match[3] / match[7], 2)
#         if win_1 > 1.15 or win_2 > 1.15:
#             if match[4] > now:
#                 diff = match[4] - now
#
#                 if diff < datetime.timedelta(minutes=2) and match[10] is False:
#                     message = (
#                         f"{match[5]}: {match[0]} - {match[1]}\n"
#                         f"D2BY: {match[2]} - {match[3]}\n"
#                         f"FanSport: {match[6]} - {match[7]}\n"
#                         f"match started at {match[4]}\n"
#                     )
#                     await send_telegram_message(message)
#                     await update_is_shown_field(match[11], {"is_shown_2": True})
#
#                 elif diff < datetime.timedelta(minutes=5) and match[9] is False:
#                     message = (
#                         f"{match[5]}: {match[0]} - {match[1]}\n"
#                         f"D2BY: {match[2]} - {match[3]}\n"
#                         f"FanSport: {match[6]} - {match[7]}\n"
#                         f"match started at {match[4]}\n"
#                     )
#                     await send_telegram_message(message)
#                     await update_is_shown_field(match[11], {"is_shown_5": True})
#
#                 elif diff < datetime.timedelta(minutes=10) and match[8] is False:
#                     message = (
#                         f"{match[5]}: {match[0]} - {match[1]}\n"
#                         f"D2BY: {match[2]} - {match[3]}\n"
#                         f"FanSport: {match[6]} - {match[7]}\n"
#                         f"match started at {match[4]}\n"
#                     )
#                     await send_telegram_message(message)
#                     await update_is_shown_field(match[11], {"is_shown_10": True})


async def delete_old_rows():
    async with async_session() as session:
        match_statement = d2by_matches.delete().where(
            text("(now() - d2by_matches.start_time) > INTERVAL '6 hours'")
        )
        await session.execute(match_statement)
        await session.commit()


async def create_tables():
    async with db.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)


async def add_fake_row():
    time = datetime.datetime(2023, 10, 25, 15, 0, 0)
    data = {
        "team_1": "davyd",
        "team_2": "davyd 2",
        "win_1": 1.47,
        "win_2": 2.48,
        "start_time": time,
    }
    await add_match_to_db(data, fan_sport_matches)


async def add_bet_type(data: dict):
    async with async_session() as session:
        select_query = bets_type.select().where(
            (bets_type.c.type == data["type"]) & (bets_type.c.order == data["order"])
        )
        try:
            result_set = await session.execute(select_query)
            t_bet = result_set.fetchone()

            return t_bet[0]
        except SQLTimeoutError:
            return
        except:
            t_bet = None

    if not t_bet:
        async with async_session() as session:
            insert_stmt = bets_type.insert().values(data)

            try:
                res = await session.execute(insert_stmt)
                await session.commit()

                return res.inserted_primary_key[0]
            except:
                pass


async def add_bet(data: dict):
    async with async_session() as session:
        select_query = bets.select().where(
            bets.c.type_id == data["type_id"],
            bets.c.match_id == data["match_id"],
        )
        try:
            result_set = await session.execute(select_query)
            bet = result_set.fetchone()
        except SQLTimeoutError:
            return
        except:
            bet = None

    if not bet:
        async with async_session() as session:
            insert_stmt = bets.insert().values(data)

            try:
                await session.execute(insert_stmt)
                await session.commit()
            except:
                return
    if data.get("d2by_1_win") and bet:
        if (
            round(data.get("d2by_1_win", 1 if bet[3] is None else float(bet[3])), 2)
            != float(1 if bet[3] is None else float(bet[3]))
            or round(data.get("d2by_2_win", 1 if bet[4] is None else float(bet[4])), 2)
            != float(1 if bet[4] is None else float(bet[4]))
        ) or (
            round(data.get("fan_1_win", 1 if bet[4] is None else float(bet[4])), 2)
            != float(1 if bet[4] is None else float(bet[4]))
            or round(data.get("fan_2_win", 1 if bet[5] is None else float(bet[5])), 2)
            != float(1 if bet[5] is None else float(bet[5]))
        ):
            async with async_session() as session:
                update_stmt = bets.update().where(bets.c.id == bet[0]).values(data)
                try:
                    await session.execute(update_stmt)
                    await session.commit()
                except:
                    return


async def get_bets_of_match(match_id: int, map_number):
    async with async_session() as session:
        type_join_stmt = bets.join(bets_type, bets.c.type_id == bets_type.c.id)
        match_join_stmt = type_join_stmt.join(
            d2by_matches, bets.c.match_id == d2by_matches.c.id
        )

        # Create the select query
        select_query = (
            select(
                *[
                    bets.c.id,
                    bets.c["values"].label("bet_values"),
                    bets_type.c.id.label("type_id"),
                    bets_type.c.fan_sport_bet_type,
                    bets_type.c.fan_sport_bet_type_football,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    bets.c.above_bets,
                ]
            )
            .select_from(match_join_stmt)
            .where((bets.c.match_id == match_id) & (bets_type.c.map == map_number))
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        return res


async def update_bet(data: dict):
    bet_id = data.pop("id")

    async with async_session() as session:
        update_stmt = bets.update().where(bets.c.id == bet_id).values(data)

        try:
            await session.execute(update_stmt)
            await session.commit()
        except SQLTimeoutError:
            return
        except:
            return


async def get_all_active_bets():
    async with async_session() as session:
        # Create the select query
        select_query = (
            select(
                *[
                    bets.c.id,
                    bets.c.d2by_1_win,
                    bets.c.d2by_2_win,
                    bets.c.fan_1_win,
                    bets.c.fan_2_win,
                    bets.c["values"].label("bet_values"),
                    bets.c.start_time,
                    bets_type.c.description,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    d2by_matches.c.game,
                    bets.c.is_shown_2,
                    bets.c.is_shown_5,
                    bets.c.is_shown_10,
                ]
            )
            .select_from(
                bets.join(bets_type, bets.c.type_id == bets_type.c.id).join(
                    d2by_matches, bets.c.match_id == d2by_matches.c.id
                )
            )
            .where(
                (func.round(bets.c.d2by_1_win / bets.c.fan_1_win, 2) > 1.15)
                | (func.round(bets.c.d2by_2_win / bets.c.fan_2_win, 2) > 1.15)
            )
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        return res


# 1. id,
# 2. d2by_1_win,
# 3. d2by_2_win,
# 4. fan_1_win,
# 5. fan_2_win,
# 6. "values"].label("bet_values"),
# 7. start_time,
# 8. description,
# 9. id.label("match_id"),
# 10. team_1,
# 11. team_2,
# 12. game,
# 13. is_shown_2,
# 14. is_shown_5,
# 15. is_shown_10,
def escape_markdown_v2(string):
    escape_chars = "_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in string)


async def send_bets_to_telegram(bets_data: list):
    now = datetime.datetime.now()
    for bet in bets_data:
        if bet[6] > now:
            diff = bet[6] - now

            if diff < datetime.timedelta(minutes=2) and bet[12] is False:
                await update_is_shown_field(bet[0], {"is_shown_2": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]

                message = (
                    f"    **{bet[11]}**    \n"
                    f"       **{bet[9]} \\- {bet[10]}**"
                    f"    **{bet[7]}:** __{bet[5]}__    \n"
                    f"__D2BY__: **{bet[1]}** \\- **{bet[2]}**\n"
                    f"__FanSport__: {bet[3]} \\- {bet[4]}\n"
                    f"Bet active until {bet[6]}\n"
                )
                await send_telegram_message(message)

            elif diff < datetime.timedelta(minutes=5) and bet[13] is False:
                await update_is_shown_field(bet[0], {"is_shown_5": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]

                message = (
                    f"    **{bet[11]}**    \n"
                    f"       **{bet[9]} \\- {bet[10]}**\n"
                    f"    **{bet[7]}:** __{bet[5]}__    \n"
                    f"__D2BY__: **{bet[1]}** \\- **{bet[2]}**\n"
                    f"__FanSport__: {bet[3]} \\- {bet[4]}\n"
                    f"Bet active until {bet[6]}\n"
                )
                await send_telegram_message(message)

            elif diff < datetime.timedelta(minutes=10) and bet[14] is False:
                await update_is_shown_field(bet[0], {"is_shown_10": True})
                bet = [escape_markdown_v2(str(i)) for i in bet]

                message = (
                    f"    **{bet[11]}**    \n"
                    f"       **{bet[9]} \\- {bet[10]}**"
                    f"    **{bet[7]}:** __{bet[5]}__    \n"
                    f"__D2BY__: **{bet[1]}** \\- **{bet[2]}**\n"
                    f"__FanSport__: {bet[3]} \\- {bet[4]}\n"
                    f"Bet active until {bet[6]}\n"
                )
                await send_telegram_message(message)
