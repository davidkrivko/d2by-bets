import pandas as pd
from sqlalchemy import Table, text, select
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from database.v1.connection import async_session
from database.v1.tables import d2by_matches, fan_sport_matches


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
            .where(
                table.c.team_1 == data["team_1"],
                table.c.team_2 == data["team_2"]
            ).limit(1)
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


async def get_d2by_matches():
    query_cols = [
        d2by_matches.c.id,
        d2by_matches.c.team_1,
        d2by_matches.c.team_2,
        d2by_matches.c.game,
        d2by_matches.c.league,
        d2by_matches.c.start_time,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "game",
        "league",
        "start_time",
    ]

    async with async_session() as session:
        select_query = select(*query_cols).select_from(d2by_matches)

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)
        matches = df.drop(columns=["league", "game"])
        matches = matches.to_dict(orient="records")

        leagues = df.groupby("game")["league"].agg(set).to_dict()

        return leagues, matches


async def get_fan_sport_matches():
    query_cols = [
        fan_sport_matches.c.id,
        fan_sport_matches.c.team_1,
        fan_sport_matches.c.team_2,
        fan_sport_matches.c.fan_ids,
        fan_sport_matches.c.start_time,
        fan_sport_matches.c.d2by_id,
        fan_sport_matches.c.sport_id,
    ]
    cols = [
        "id",
        "team_1",
        "team_2",
        "fan_ids",
        "start_time",
        "d2by_id",
        "sport_id"
    ]

    async with async_session() as session:
        select_query = select(*query_cols).select_from(fan_sport_matches)

        try:
            result_set = await session.execute(select_query)
            res = result_set.fetchall()
        except SQLTimeoutError:
            return []

        df = pd.DataFrame(columns=cols, data=res)

        return df.to_dict(orient="records")
