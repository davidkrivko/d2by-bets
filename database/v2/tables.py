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
from sqlalchemy.dialects.postgresql import JSONB

from database.v2.connection import meta_2


d2by_matches = Table(
    "d2by_matches",
    meta_2,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("start_time", TIMESTAMP),
    Column("game", String),
    Column("team_1_short", String, nullable=True),
    Column("team_2_short", String, nullable=True),
    Column("d2by_id", String, nullable=True),
    Column("d2by_url", String, nullable=True),
    extend_existing=True,
)


fan_sport_matches = Table(
    "fan_sport_matches",
    meta_2,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("team_1", String),
    Column("team_2", String),
    Column("fan_ids", String),
    Column("start_time", TIMESTAMP),
    Column("d2by_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE"), unique=True),
    extend_existing=True,
)


bets_type = Table(
    "bets_type",
    meta_2,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("type", String),
    Column("description", String),
    Column("fan_sport_bet_type", String, nullable=True),
    Column("fan_sport_bet_type_football", String, nullable=True),
    extend_existing=True,
)


bets_table = Table(
    "bets",
    meta_2,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("isActive", Boolean),
    Column("value", Numeric(precision=5, scale=1)),
    Column("extra", String, nullable=True),
    Column("d2by_bets", JSONB, default={}),
    Column("fan_bets", JSONB, default={}),
    Column("d2by_probs", JSONB, default={}),
    Column("bet_id", String),
    Column("start_time", TIMESTAMP),
    Column("type_id", ForeignKey(bets_type.c.id, ondelete="CASCADE")),
    Column("match_id", ForeignKey(d2by_matches.c.id, ondelete="CASCADE")),
    Column("above_bets", Integer, nullable=True),
    Column("map_v2", Integer, nullable=True),
    Column("d2by_id", String),
    Column("fan_url", String, nullable=True),
    Column("is_shown", Boolean, default=False),
    extend_existing=True,
)
