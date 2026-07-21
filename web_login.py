from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils.logger import logging

from config import (
    WAIT_TIMEOUT,
    DOWNLOAD_BUTTON,
    EMAIL_INPUT,
    CONTINUE_BUTTON,
    CHECKBOX_LABEL,
    CHECKBOX,
    OTP_INPUTS,
    VERIFY_BUTTON,
)


def click_initial_download(driver):
    try:
        btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located(DOWNLOAD_BUTTON)
        )
        btn.click()
        logging.info("Clicked 'Download for Free' button.")
        return True
    except Exception as e:
        logging.error(f"Failed to click download button: {e}")
        return False


def handle_email_input(driver, email):
    try:
        email_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located(EMAIL_INPUT)
        )
        email_field.clear()
        email_field.send_keys(email)
        time.sleep(0.5)

        continue_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(CONTINUE_BUTTON)
        )
        continue_btn.click()
        logging.info("Clicked 'Continue with email'.")
        return True
    except Exception as e:
        logging.error(f"Failed to handle email input: {e}")
        return False


def check_verification(driver, target, timeout):
    for i in range(timeout):
        logging.info(
            f"Checking if target URL {target} is reached. Check {i+1}/{timeout}"
        )
        if target in driver.current_url:
            logging.info(f"{target} URL reached successfully.")
            return True
        time.sleep(1)
    return False


def handle_captcha(driver, manual_check):
    target_url_part = "#/code-validation"
    check_verification(driver, target=target_url_part, timeout=3)
    try:
        checkbox_label = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(CHECKBOX_LABEL)
        )
        checkbox = checkbox_label.find_element(CHECKBOX)
        if not checkbox.is_selected():
            checkbox.click()
            logging.info("Clicked the captcha checkbox.")
            check_verification(driver, target=target_url_part, timeout=5)
    except Exception as e:
        logging.warning(f"Automated captcha checkbox handling skipped or failed.")
    if not check_verification(driver, target=target_url_part, timeout=3):
        logging.warning(
            "Verification page not reached. Please solve the captcha manually in the browser."
        )
        if manual_check:
            while not check_verification(driver, target=target_url_part, timeout=1):
                input(
                    "Press Enter HERE in the terminal AFTER you have completed the captcha/login in the browser..."
                )
                if check_verification(driver, target=target_url_part, timeout=1):
                    return True
                else:
                    print(
                        "Target validation page still not detected. Please try completing it again."
                    )
        else:
            return False
    return True


def web_login_flow(driver, headless, email):
    try:
        if not click_initial_download(driver):
            return False

        if not handle_email_input(driver, email):
            return False

        if not handle_captcha(driver, not headless):
            return False

        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located(OTP_INPUTS[0])
        )
        return True
    except Exception as e:
        logging.error(f"Error in web login flow: {e}")
        return False


def submit_otp(driver, otp):
    try:
        target_url_part = "#/account-activated-success"
        for i, digit in enumerate(otp):
            input_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_element_located(OTP_INPUTS[i])
            )
            input_field.clear()
            input_field.send_keys(digit)
            time.sleep(0.1)

        verify_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable(VERIFY_BUTTON)
        )
        verify_btn.click()
        logging.info("OTP submitted and Verify clicked.")

        timeout = 5
        start_time = time.time()
        while time.time() - start_time < timeout:
            if target_url_part in driver.current_url:
                logging.info("Account Activated Successfully.")
                return True
            time.sleep(0.5)
        return False
    except Exception as e:
        logging.error(f"OTP submission failed: {e}")
        return False
