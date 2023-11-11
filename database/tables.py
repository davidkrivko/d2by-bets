from sqlalchemy import (
    Table,
    Column,
    String,
    Numeric,
    Integer,
    TIMESTAMP,
    Boolean,
    ForeignKey,
)

from database.connection import meta, db

d2by_matches = Table(
    "d2by_matches",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("start_time", TIMESTAMP),
    Column("game", String),
    Column("league", String, nullable=True),
    extend_existing=True,
)


fan_sport_matches = Table(
    "fan_sport_matches",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("start_time", TIMESTAMP),
    Column("d2by_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE"), unique=True),
    extend_existing=True,
)


bets_type = Table(
    "bets_type",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String),
    Column("order", Integer),
    Column("description", String),
    Column("fan_sport_bet_type", String, nullable=True),
    Column("fan_sport_bet_type_football", String, nullable=True),
    Column("map", Integer, nullable=True),
    extend_existing=True,
)


bets = Table(
    "bets",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("isActive", Boolean),
    Column("values", Numeric(precision=5, scale=1)),
    Column("d2by_1_win", Numeric(precision=5, scale=2)),
    Column("d2by_2_win", Numeric(precision=5, scale=2)),
    Column("fan_1_win", Numeric(precision=5, scale=2), nullable=True),
    Column("fan_2_win", Numeric(precision=5, scale=2), nullable=True),
    Column("type_id", ForeignKey(bets_type.c.id, ondelete="CASCADE")),
    Column("match_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE")),
    Column("above_bets", Integer),
    Column("start_time", TIMESTAMP),
    Column("is_shown_10", Boolean, default=False),
    Column("is_shown_5", Boolean, default=False),
    Column("is_shown_2", Boolean, default=False),
    extend_existing=True,
)


async def create_tables():
    async with db.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)
