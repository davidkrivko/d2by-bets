import os
from dotenv import load_dotenv

load_dotenv()


DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")


TIME_DELTA = os.environ.get("TIME_DELTA", 0)
THRESHOLD = 60
WORD_BLACK_LIST = ["vfl", "gaming", "esports", "ac", "fc", "esport", "team"]

TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT")
CHAT_ID = os.environ.get("CHAT_ID")
