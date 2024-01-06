import os
from dotenv import load_dotenv
# from simplegmail import Gmail
#
# from login.api import get_token

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
SENDING_MESSAGES_DELTA = int(os.environ.get("SENDING_MESSAGES_DELTA", 0))

THRESHOLD = 60
WORD_BLACK_LIST = ["vfb", "vfl", "gaming", "esports", "ac", "fc", "esport", "team", "bitskins", "vincere"]


TELEGRAM_BOT = os.environ.get("TELEGRAM_BOT")
CHAT_ID = os.environ.get("CHAT_ID")

USERNAME = os.environ.get("LOGIN_USERNAME")
PASSWORD = os.environ.get("LOGIN_PASSWORD")

# GMAIL_CLIENT = Gmail()
# AUTH_TOKEN = get_token(USERNAME, PASSWORD)
