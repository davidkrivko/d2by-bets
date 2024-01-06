from sqlalchemy import and_, select

from database.v2.connection import async_session_2 as async_session
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v2.tables import bets_table, bets_type, d2by_matches


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


def compare_bet_cfs_v2(data, bet):
    return (
        data.get("d2by_bets") != bet[4]
        or bet[1] != data["isActive"]
    )


async def add_bet(data: dict):
    async with async_session() as session:
        try:
            select_query = bets_table.select().where(
                and_(
                    bets_table.c.type_id == data["type_id"],
                    bets_table.c.match_id == data["match_id"],
                    bets_table.c.value == data.get("value"),
                    bets_table.c.map_v2 == data.get("map_v2"),
                    bets_table.c.above_bets == data.get("above_bets"),
                    bets_table.c.extra == data.get("extra"),
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
                if compare_bet_cfs_v2(data, bet):
                    data["is_shown"] = False

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

        # Create the select query
        select_query = (
            select(
                *[
                    bets_table.c.id,
                    bets_table.c.d2by_bets,
                    bets_table.c.map_v2,
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
                & (bets_table.c.map_v2 == map_number)
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
                    bets_table.c.d2by_bets,
                    bets_table.c.fan_bets,
                    bets_table.c["value"].label("bet_values"),
                    bets_table.c.start_time,
                    bets_type.c.description,
                    d2by_matches.c.id.label("match_id"),
                    d2by_matches.c.team_1,
                    d2by_matches.c.team_2,
                    d2by_matches.c.game,
                    bets_table.c.above_bets,
                    d2by_matches.c.d2by_url,
                    bets_table.c.fan_url,
                ]
            )
            .select_from(
                bets_table.join(
                    bets_type, bets_table.c.type_id == bets_type.c.id
                ).join(d2by_matches, bets_table.c.match_id == d2by_matches.c.id)
            )
            .where(
                (bets_table.c.fan_bets != {})
                & (bets_table.c.isActive == True)
                & (bets_table.c.is_shown == False)
            )
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []
        except Exception as e:
            pass

        return res


async def is_shown_update(ids):
    async with async_session() as session:
        update_stmt = bets_table.update().where(bets_table.c.id.in_(ids)).values(is_shown=True)

        try:
            await session.execute(update_stmt)
            await session.commit()
        except SQLTimeoutError:
            return
        except Exception as e:
            return
