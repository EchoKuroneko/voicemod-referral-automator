import time
import re
from dotenv import load_dotenv, set_key
import os

from utils.logger import logging
from mail_tm import create_temp_account, get_otp, delete_temp_account
from browser import open_browser, close_browser
from web_login import web_login_flow, submit_otp
from voicemod import launch_voicemod_app, check_voicemod_installation

load_dotenv()
LOGIN_URL = os.getenv("LOGIN_URL")


def validate_login_url(url):
    if "<invite_id>" in url:
        return False

    pattern = r"^https://voicemod\.net/friend/[a-f0-9]+$"
    return bool(re.match(pattern, url))


def save_login_url(url):
    set_key(".env", "LOGIN_URL", url)
    logging.info("Saved LOGIN_URL to .env")


def clean_up(driver, account):
    close_browser(driver)
    delete_temp_account(account)


def run_cycles(iterations, headless):
    if not check_voicemod_installation():
        return

    login_url = LOGIN_URL
    driver = None
    try:
        for cycle in range(iterations):
            logging.info(f"===== Starting cycle {cycle+1} =====")

            if not login_url or not validate_login_url(login_url):
                logging.error("LOGIN_URL is missing.")
                login_url = input("Enter your invite link:\n").strip()

                if validate_login_url(login_url):
                    save_login_url(login_url)
                else:
                    logging.error(
                        "Invalid LOGIN_URL.\n"
                        "\t\t\t\t  Expected format:\n"
                        "\t\t\t\t  https://voicemod.net/friend/<invite_id>"
                    )
                    exit()

            account = create_temp_account()

            if not account:
                continue

            driver = open_browser(login_url, headless)

            if not web_login_flow(driver, headless, account.address):
                close_browser(driver)
                driver = open_browser(login_url)
                if headless and not web_login_flow(
                    driver, not headless, account.address
                ):
                    clean_up(driver, account)
                    driver = None
                    continue

            otp = get_otp(account)
            if not otp:
                logging.error("OTP not retrieved.")
                clean_up(driver, account)
                driver = None
                continue

            if not submit_otp(driver, otp):
                clean_up(driver, account)
                driver = None
                continue

            if not launch_voicemod_app(driver):
                clean_up(driver, account)
                driver = None
                continue

            clean_up(driver, account)
            driver = None

            logging.info(f"===== Cycle {cycle+1} completed =====\n")
            time.sleep(3)

    except KeyboardInterrupt:
        pass

    finally:
        if driver:
            close_browser(driver)


if __name__ == "__main__":
    run_cycles(iterations=5, headless=False)
