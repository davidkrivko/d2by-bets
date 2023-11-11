import asyncio
from script import main

from database.tables import create_tables


if __name__ == "__main__":
    asyncio.run(main())
