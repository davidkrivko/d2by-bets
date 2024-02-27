import os
from dotenv import load_dotenv

load_dotenv()


DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

DB2_USER = os.environ.get("DB2_USER")
DB2_PASSWORD = os.environ.get("DB2_PASS")
DB2_HOST = os.environ.get("DB2_HOST")
DB2_PORT = os.environ.get("DB2_PORT")
DB2_NAME = os.environ.get("DB2_NAME")

D2BY_TIME_DELTA = int(os.environ.get("D2BY_TIME_DELTA", 0))
FAN_SPORT_DELTA = int(os.environ.get("FAN_SPORT_DELTA", 0))
SENDING_MESSAGES_DELTA = int(os.environ.get("SENDING_MESSAGES_DELTA", 0))

THRESHOLD = 60
WORD_BLACK_LIST = [
    "vfb",
    "vfl",
    "gaming",
    "esports",
    "ac",
    "fc",
    "esport",
    "team",
    "bitskins",
    "vincere",
    "challengers",
]


TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT")
CHAT_ID = os.environ.get("CHAT_ID")

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

IS_ALL_MATCHES = bool(os.environ.get("IS_ALL_MATCHES", 0))

DEFAULT_D2BY_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://d2by.com",
        "referer": "https://d2by.com/",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }

DEFAULT_FAN_HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://fan-sport.cc",
        "referer": "https://fan-sport.cc/",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    }
