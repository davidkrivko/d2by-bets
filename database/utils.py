from database.v1.connection import db, meta
from database.v2.connection import db_2, meta_2


async def create_tables(database, meta):
    async with database.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)


async def create_all_tables():
    async with db.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

    async with db_2.begin() as conn:
        await conn.run_sync(meta_2.drop_all)
        await conn.run_sync(meta_2.create_all)
