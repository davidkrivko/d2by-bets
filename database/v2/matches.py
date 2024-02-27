import pandas as pd
from sqlalchemy import Table, text, select, func, and_
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v2.connection import async_session_2 as async_session
from database.v2.tables import d2by_matches, fan_sport_matches


async def delete_old_rows():
    async with async_session() as session:
        match_statement = d2by_matches.delete().where(
            text("(now() - d2by_matches.start_time) > INTERVAL '6 hours'")
        )
        await session.execute(match_statement)
        await session.commit()


async def add_match_to_db(data: dict, table: Table):
    async with async_session() as session:
        match_statement = (
            table.select()
            .where(table.c.team_1 == data["team_1"], table.c.team_2 == data["team_2"])
            .limit(1)
        )
        try:
            result_set = await session.execute(match_statement)

            match = result_set.fetchone()
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

                data["id"] = res.inserted_primary_key[0]
                return data
            except SQLTimeoutError:
                return
            except Exception as e:
                pass
    else:
        async with async_session() as session:
            update_stmt = table.update().where(table.c.id == match[0]).values(data)

            try:
                await session.execute(update_stmt)
                await session.commit()

                data["id"] = match[0]
                return data
            except SQLTimeoutError:
                return
            except Exception as e:
                pass


async def get_d2by_live_matches():
    query_cols = [
        d2by_matches.c.id,
        d2by_matches.c.team_1,
        d2by_matches.c.team_2,
        d2by_matches.c.team_1_short,
        d2by_matches.c.team_2_short,
        d2by_matches.c.start_time,
        d2by_matches.c.d2by_id,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "team_1_short",
        "team_2_short",
        "start_time",
        "d2by_id",
    ]

    fifteen_minutes_ago = func.now() - text("INTERVAL '15 minutes'")

    async with async_session() as session:
        select_query = (
            select(*query_cols)
            .select_from(d2by_matches)
            .where(d2by_matches.c.start_time <= fifteen_minutes_ago)
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)

        return df.to_dict(orient="records")


async def get_d2by_line_matches(is_all: bool = False):
    query_cols = [
        d2by_matches.c.id,
        d2by_matches.c.team_1,
        d2by_matches.c.team_2,
        d2by_matches.c.team_1_short,
        d2by_matches.c.team_2_short,
        d2by_matches.c.start_time,
        d2by_matches.c.d2by_id,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "team_1_short",
        "team_2_short",
        "start_time",
        "d2by_id",
    ]

    fifteen_minutes_ago = func.now() - text("INTERVAL '15 minutes'")
    three_hours_more = func.now() + text("INTERVAL '3 hours'")

    async with async_session() as session:
        if is_all:
            select_query = (
                select(*query_cols)
                .select_from(d2by_matches)
                .where(
                    d2by_matches.c.start_time > fifteen_minutes_ago,
                )
            )
        else:
            select_query = (
                select(*query_cols)
                .select_from(d2by_matches)
                .where(
                    and_(
                        d2by_matches.c.start_time > fifteen_minutes_ago,
                        d2by_matches.c.start_time < three_hours_more
                    )
                )
            )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)

        return df.to_dict(orient="records")


async def get_fan_sport_live_matches():
    query_cols = [
        fan_sport_matches.c.id,
        fan_sport_matches.c.team_1,
        fan_sport_matches.c.team_2,
        fan_sport_matches.c.fan_ids,
        fan_sport_matches.c.start_time,
        fan_sport_matches.c.d2by_id,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "fan_ids",
        "start_time",
        "d2by_id",
    ]

    fifteen_minutes_ago = func.now() - text("INTERVAL '15 minutes'")

    async with async_session() as session:
        select_query = (
            select(*query_cols)
            .select_from(fan_sport_matches)
            .where(fan_sport_matches.c.start_time <= fifteen_minutes_ago)
        )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)

        return df.to_dict(orient="records")


async def get_fan_sport_line_matches(is_all: bool = False):
    query_cols = [
        fan_sport_matches.c.id,
        fan_sport_matches.c.team_1,
        fan_sport_matches.c.team_2,
        fan_sport_matches.c.fan_ids,
        fan_sport_matches.c.start_time,
        fan_sport_matches.c.d2by_id,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "fan_ids",
        "start_time",
        "d2by_id",
    ]

    fifteen_minutes_ago = func.now() - text("INTERVAL '15 minutes'")
    three_hours_more = func.now() + text("INTERVAL '3 hours'")

    async with async_session() as session:
        if is_all:
            select_query = (
                select(*query_cols)
                .select_from(fan_sport_matches)
                .where(
                    d2by_matches.c.start_time > fifteen_minutes_ago,
                )
            )
        else:
            select_query = (
                select(*query_cols)
                .select_from(fan_sport_matches)
                .where(
                    and_(
                        d2by_matches.c.start_time > fifteen_minutes_ago,
                        d2by_matches.c.start_time < three_hours_more
                    )
                )
            )

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)

        return df.to_dict(orient="records")
