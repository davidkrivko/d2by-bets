import os
import sys
import asyncio

current_directory = os.path.dirname(os.path.realpath(__file__))

# Get the root directory of the current script's directory
parent_directory = os.path.dirname(current_directory)
root_directory = os.path.dirname(parent_directory)

# Add the parent directory to sys.path
sys.path.append(root_directory)


from sport.api import collect_d2by_sport_matches


asyncio.run(collect_d2by_sport_matches())
