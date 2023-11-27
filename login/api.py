import datetime
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from login.emails import get_verification_code


CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_argument("--window-size=1300,800")


def get_token():
    driver = webdriver.Chrome(options=CHROME_OPTIONS)
    driver.get("https://d2by.com/")

    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".modal-select-items.d2by-deposit-withdraw")
        )
    )

    login_button = driver.find_element(
        By.CSS_SELECTOR,
        ".bg-orange-ff9910.rounded.text-white.py-1.px-6.text-sm.cursor-pointer.font-arial",
    )
    login_button.click()

    email_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")

    email_input.send_keys("davidkrivko@gmail.com")
    password_input.send_keys("QPty2002")

    # Click the login button
    time = datetime.datetime.utcnow()

    login_button = driver.find_element(By.CSS_SELECTOR, ".button.to-yellow-f9b80e")
    login_button.click()

    ver_code = get_verification_code(time)

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

    driver.close()
    for ck in cookies:
        if ck["name"] == "_cus_token":
            return {"name": ck["name"], "value": ck["value"]}
