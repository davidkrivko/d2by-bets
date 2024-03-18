import asyncio
from dotenv import load_dotenv

load_dotenv()

from database.utils import create_all_tables
from scripts import update_all_bets

if __name__ == "__main__":
    bets =  asyncio.run(update_all_bets())
