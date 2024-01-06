from sqlalchemy import and_, select, func

from database.v1.connection import async_session
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v1.tables import bets_table, bets_type, d2by_matches


async def add_bet_type(data: dict):
    async with async_session() as session:
        try:
            select_query = bets_type.select().where(bets_type.c.type == data["type"])
            result_set = await session.execute(select_query)
            t_bet = result_set.fetchone()

            if t_bet:
                data["id"] = t_bet[0]
                return data
            else:
                insert_stmt = bets_type.insert().values(data)
                res = await session.execute(insert_stmt)
                await session.commit()

                data["id"] = res.inserted_primary_key[0]
                return data
        except SQLTimeoutError:
            return await add_bet_type(data)
        except Exception as e:
            return


def compare_bet_cfs(data, bet):
    return (
        (
            round(data.get("d2by_1_win", 1 if bet[3] is None else float(bet[3])), 2)
            != float(1 if bet[3] is None else float(bet[3]))
            or round(data.get("d2by_2_win", 1 if bet[4] is None else float(bet[4])), 2)
            != float(1 if bet[4] is None else float(bet[4]))
        )
        or (
            round(data.get("fan_1_win", 1 if bet[4] is None else float(bet[4])), 2)
            != float(1 if bet[4] is None else float(bet[4]))
            or round(data.get("fan_2_win", 1 if bet[5] is None else float(bet[5])), 2)
            != float(1 if bet[5] is None else float(bet[5]))
        )
        or (data.get("isActive") != bet[1])
    )


async def add_bet(data: dict):
    async with async_session() as session:
        try:

            select_query = bets_table.select().where(
                and_(
                    bets_table.c.type_id == data["type_id"],
                    bets_table.c.match_id == data["match_id"],
                    bets_table.c.value == data.get("value"),
                    bets_table.c.above_bets == data.get("above_bets"),
                ),
            )

            result_set = await session.execute(select_query)
            bet = result_set.fetchone()
        except Exception as e:
            return

        try:
            # If bet does not exist, insert it
            if not bet:
                insert_stmt = bets_table.insert().values(data)
                await session.execute(insert_stmt)
            elif bet:
                if compare_bet_cfs(data, bet):
                    update_stmt = (
                        bets_table.update().where(bets_table.c.id == bet[0]).values(data)
                    )
                    await session.execute(update_stmt)

            await session.commit()
        except SQLTimeoutError:
            return await add_bet(data)


async def get_bets_of_match(match_id: int, map_number):
    async with async_session() as session:
        type_join_stmt = bets_table.join(
            bets_type, bets_table.c.type_id == bets_type.c.id
        )
        match_join_stmt = type_join_stmt.join(
            d2by_matches, bets_table.c.match_id == d2by_matches.c.id
        )

        select_query = (
            select(
                *[
                    bets_table.c.id,
                    bets_table.c["value"].label("bet_values"),
                    bets_type.c.id.label("type_id"),
                    bets_type.c.fan_sport_bet_type,
                    bets_type.c.fan_sport_bet_type_football,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    bets_table.c.above_bets,
                    bets_type.c.description,
                ]
            )
            .select_from(match_join_stmt)
            .where(
                (bets_table.c.match_id == match_id)
                & (bets_type.c.map == map_number)
                & (bets_table.c.isActive == True)
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
        update_stmt = bets_table.update().where(bets_table.c.id == bet_id).values(data)

        try:
            await session.execute(update_stmt)
            await session.commit()
        except SQLTimeoutError:
            return
        except Exception as e:
            return


async def get_all_active_bets():
    async with async_session() as session:
        select_query = (
            select(
                *[
                    bets_table.c.id,
                    bets_table.c.d2by_1_win,
                    bets_table.c.d2by_2_win,
                    bets_table.c.fan_1_win,
                    bets_table.c.fan_2_win,
                    bets_table.c["value"].label("bet_values"),
                    bets_table.c.start_time,
                    bets_type.c.description,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    d2by_matches.c.game,
                    bets_table.c.is_shown_2,
                    bets_table.c.is_shown_5,
                    bets_table.c.is_shown_10,
                    bets_table.c.above_bets,
                    bets_table.c.amount_1_win,
                    bets_table.c.amount_2_win,
                    bets_table.c.d2by_url,
                    bets_table.c.fan_url,
                ]
            )
            .select_from(
                bets_table.join(
                    bets_type, bets_table.c.type_id == bets_type.c.id
                ).join(d2by_matches, bets_table.c.match_id == d2by_matches.c.id)
            )
            .where(
                (
                    (
                        func.round(bets_table.c.d2by_1_win / bets_table.c.fan_1_win, 2)
                        > 1.15
                    )
                    | (
                        func.round(bets_table.c.d2by_2_win / bets_table.c.fan_2_win, 2)
                        > 1.15
                    )
                )
                & (bets_table.c.isActive == True)
            )
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        return res


async def update_is_shown_field(bet_id: int, data: dict):
    async with async_session() as session:
        update_stmt = bets_table.update().where(bets_table.c.id == bet_id).values(data)
        try:
            await session.execute(update_stmt)
            await session.commit()
        except SQLTimeoutError:
            return
        except:
            return
