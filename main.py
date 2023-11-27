import asyncio

from database.tables import create_tables
from roulette.script import roulette
from parcing.script import main, test_v2_api

if __name__ == "__main__":
    asyncio.run(roulette())
