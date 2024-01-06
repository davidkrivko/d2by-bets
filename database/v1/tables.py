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

from database.v1.connection import meta

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
    Column("fan_ids", String),
    Column("sport_id", Integer),
    Column("start_time", TIMESTAMP),
    Column("d2by_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE"), unique=True),
    extend_existing=True,
)


bets_type = Table(
    "bets_type",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String),
    Column("description", String),
    Column("fan_sport_bet_type", String, nullable=True),
    Column("fan_sport_bet_type_football", String, nullable=True),
    Column("map", Integer, nullable=True),
    extend_existing=True,
)


bets_table = Table(
    "bets",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("isActive", Boolean),
    Column("value", Numeric(precision=5, scale=1)),
    Column("d2by_1_win", Numeric(precision=5, scale=3)),
    Column("d2by_2_win", Numeric(precision=5, scale=3)),
    Column("fan_1_win", Numeric(precision=5, scale=3), nullable=True),
    Column("fan_2_win", Numeric(precision=5, scale=3), nullable=True),
    Column("type_id", ForeignKey(bets_type.c.id, ondelete="CASCADE")),
    Column("match_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE")),
    Column("above_bets", Integer, nullable=True),
    Column("start_time", TIMESTAMP),
    Column("amount_1_win", Numeric(precision=5, scale=2), nullable=True),
    Column("amount_2_win", Numeric(precision=5, scale=2), nullable=True),
    Column("d2by_id", String),
    Column("d2by_url", String),
    Column("fan_url", String, nullable=True),
    Column("is_shown_10", Boolean, default=False),
    Column("is_shown_5", Boolean, default=False),
    Column("is_shown_2", Boolean, default=False),
    extend_existing=True,
)
