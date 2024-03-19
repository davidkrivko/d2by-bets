import datetime
import logging
import os
import json
import aiohttp
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import USERNAME, PASSWORD
from login.emails import get_verification_code

from config import DEFAULT_D2BY_HEADERS
from telegram import send_telegram_message_v2


CHROME_OPTIONS = webdriver.ChromeOptions()


CHROME_OPTIONS.add_argument("--window-size=1300,800")
if os.environ.get("CHROME_OPTIONS") == "true":
    CHROME_OPTIONS.add_argument("--disable-gpu")
    CHROME_OPTIONS.add_argument("--headless")
    CHROME_OPTIONS.add_argument("--no-sandbox")
    CHROME_OPTIONS.add_argument("--disable-dev-shm-usage")


def get_token(username, password, gmail_client):
    logging.error("Start login")
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    driver.get("https://d2by.com/")

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".modal-select-items.d2by-deposit-withdraw")
        )
    )

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".bg-orange-ff9910.rounded.text-white.py-1.px-6.text-sm.cursor-pointer.font-arial")
        )
    )
    login_button = driver.find_element(
        By.CSS_SELECTOR,
        ".bg-orange-ff9910.rounded.text-white.py-1.px-6.text-sm.cursor-pointer.font-arial",
    )
    login_button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "email")
        )
    )
    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys(username)
    password_input.send_keys(password)

    # Click the login button
    time = datetime.datetime.utcnow()

    login_button = driver.find_element(By.CSS_SELECTOR, ".button.to-yellow-f9b80e")
    login_button.click()

    ver_code = get_verification_code(time, gmail_client)
    if ver_code is None:
        return get_token(username, password, gmail_client)

    wait = WebDriverWait(driver, 20)
    wait.until(
        EC.presence_of_element_located(
            (By.NAME, "verifyCode")
        )
    )
    code_input = driver.find_element(By.NAME, "verifyCode")
    code_input.send_keys(ver_code)

    login_button.click()

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".font-bold.border-yellow-f99910")
        )
    )

    cookies = driver.get_cookies()

    logging.error("Get cookies")
    driver.close()
    for ck in cookies:
        if ck["name"] == "_cus_token":
            return {"name": ck["name"], "value": ck["value"]}


async def create_new_token(gmail_client):
    new_token = get_token(username=USERNAME, password=PASSWORD, gmail_client=gmail_client)
    global AUTH_TOKEN
    AUTH_TOKEN = new_token

    return AUTH_TOKEN


async def get_balance(auth_token):
    headers = DEFAULT_D2BY_HEADERS
    headers["Authorization"] = f"Bearer {auth_token['value']}"

    async with aiohttp.ClientSession(cookies=[auth_token], headers=headers) as session:
        async with session.get(
            "https://api.d2by.com/api/v1/web/user/profile",
            ssl=False
        ) as resp:
            response = await resp.text()
            response = json.loads(response)

            if response["meta"]["status"] == 200:
                gold = round(response["data"]["coin"]["gold"], 2)
                gem = round(response["data"]["coin"]["gem"], 2)
                diamond = round(response["data"]["coin"]["diamond"], 2)

                message = f"GOLD: {gold}\nDIAMOND: {diamond}\nGEM: {gem}"

                await send_telegram_message_v2(message)
