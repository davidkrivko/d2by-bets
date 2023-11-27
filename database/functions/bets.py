from sqlalchemy import func
from sqlalchemy.sql import select
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.connection import async_session
from database.tables import d2by_matches, bets_type, bets


async def add_bet_type(data: dict, bets_table):
    async with async_session() as session:
        try:
            select_query = bets_table.select().where(bets_table.c.type == data["type"])
            result_set = await session.execute(select_query)
            t_bet = result_set.fetchone()

            if t_bet:
                data["id"] = t_bet[0]
                return data
            else:
                insert_stmt = bets_table.insert().values(data)
                res = await session.execute(insert_stmt)
                await session.commit()

                data["id"] = res.inserted_primary_key[0]
                return data
        except SQLTimeoutError:
            return await add_bet_type(data, bets_table)
        except Exception as e:
            return


async def add_bet(data: dict):
    async with async_session() as session:
        try:
            # Check if the bet exists
            select_query = bets.select().where(
                bets.c.type_id == data["type_id"],
                bets.c.match_id == data["match_id"],
                bets.c.values == data["values"],
                bets.c.extra == data["extra"],
                )
            result_set = await session.execute(select_query)
            bet = result_set.fetchone()

            # If bet does not exist, insert it
            if not bet:
                insert_stmt = bets.insert().values(data)
                await session.execute(insert_stmt)
            elif bet:
                if (
                    (
                        round(data.get("d2by_1_win", 1 if bet[3] is None else float(bet[3])), 2)
                        != float(1 if bet[3] is None else float(bet[3]))
                        or round(
                            data.get("d2by_2_win", 1 if bet[4] is None else float(bet[4])), 2
                        )
                        != float(1 if bet[4] is None else float(bet[4]))
                    )
                    or (
                        round(data.get("fan_1_win", 1 if bet[4] is None else float(bet[4])), 2)
                        != float(1 if bet[4] is None else float(bet[4]))
                        or round(
                            data.get("fan_2_win", 1 if bet[5] is None else float(bet[5])), 2
                        )
                        != float(1 if bet[5] is None else float(bet[5]))
                    )
                    or (data.get("isActive") != bet[1])
                ):
                    update_stmt = bets.update().where(bets.c.id == bet[0]).values(data)
                    await session.execute(update_stmt)

            await session.commit()
        except SQLTimeoutError:
            return
        except Exception as e:
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
                    bets_type.c.description,
                ]
            )
            .select_from(match_join_stmt)
            .where(
                (bets.c.match_id == match_id)
                & (bets_type.c.map == map_number)
                & (bets.c.isActive == True)
            )
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
                    bets.c.above_bets,
                    bets.c.amount_1_win,
                    bets.c.amount_2_win,
                    bets.c.d2by_url,
                    bets.c.fan_url,
                ]
            )
            .select_from(
                bets.join(bets_type, bets.c.type_id == bets_type.c.id).join(
                    d2by_matches, bets.c.match_id == d2by_matches.c.id
                )
            )
            .where(
                (
                    (func.round(bets.c.d2by_1_win / bets.c.fan_1_win, 2) > 1.15)
                    | (func.round(bets.c.d2by_2_win / bets.c.fan_2_win, 2) > 1.15)
                )
                & (bets.c.isActive == True)
            )
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        return res
