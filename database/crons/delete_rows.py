import os
import sys
import asyncio

current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of the current script's directory
parent_directory = os.path.dirname(current_directory)
root_directory = os.path.dirname(parent_directory)

# Add the parent directory to sys.path
sys.path.append(root_directory)

from database.v1.matches import delete_old_rows as delete_old_rows_v1
from database.v2.matches import delete_old_rows as delete_old_rows_v2


async def delete_rows():
    await delete_old_rows_v1()
    await delete_old_rows_v2()


asyncio.run(delete_rows())
