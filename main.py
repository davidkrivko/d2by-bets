import asyncio

from database.utils import create_all_tables
from scripts import update_all_bets

if __name__ == "__main__":
    asyncio.run(update_all_bets())
