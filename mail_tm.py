from mailpytm import MailTMApi
from mailpytm.mailpytm import MailTMAccount
import re
from utils.logger import logging
import time


def create_temp_account():
    try:
        account = MailTMApi.create_email()
        logging.info(f"Created temp email: {account.address}")
        return account
    except Exception as e:
        logging.error(f"Failed to create temp email: {e}")
        return None


def get_latest_message(account):
    messages = account.messages
    return messages[0] if messages else None


def get_full_message(account):
    message = get_latest_message(account)
    if not message:
        return None
    return account.get_message_by_id(message["id"])


def extract_otp(text):
    match = re.search(r"\b(\d{6}\b)", text)
    if match:
        otp = match.group(1)
        logging.info(f"OTP: {otp}")
        return otp
    return None


def get_otp(account, timeout=60, poll_interval=5):
    logging.info("Checking for messages...")
    try:
        start = time.time()
        while time.time() - start < timeout:
            latest_message = get_latest_message(account)
            otp = extract_otp(latest_message["subject"])
            if otp:
                return otp
            time.sleep(poll_interval)
        return None
    except Exception as e:
        logging.error(f"Mail fetch error: {e}")
        return None


def delete_temp_account(account):
    try:
        account.delete_account()
        logging.info("Temp account deleted.")
    except Exception as e:
        logging.error(f"Account deletion error: {e}")
