import undetected_chromedriver as uc
import psutil

from utils.logger import logging
from config import BASE_URL, CHROME_VERSION

uc.Chrome.__del__ = lambda self: None


def open_browser(url, headless=False):
    driver = None
    try:
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )

        if headless:
            options.add_argument("--headless=new")

        prefs = {
            "download.default_directory": "NUL",  # Sends any forced download into a black hole (Windows)
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
            "protocol_handler.allowed_origin_protocol_pairs": {
                BASE_URL: {"voicemod": True}
            },
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument("--disable-features=DownloadService")
        driver = uc.Chrome(options=options, version_main=CHROME_VERSION)
        if headless:
            logging.info("Browser started in HEADLESS mode.")
        else:
            driver.maximize_window()
            logging.info("Browser started in VISIBLE mode.")
        driver.get(url)
        return driver
    except KeyboardInterrupt:
        logging.warning("Interrupted during browser startup.")
        if driver:
            close_browser(driver)
        raise


def close_browser(driver):
    if driver is None:
        return
    logging.info("Cleaning up automation session...")
    try:
        pid = driver.service.process.pid
    except Exception:
        pid = None

    try:
        driver.quit()
    except Exception as e:
        logging.warning(f"driver.quit() failed: {e}")

    if pid and psutil.pid_exists(pid):
        try:
            logging.warning("Chromedriver still alive. Killing...")
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        except Exception as e:
            logging.warning(f"Failed to kill process tree: {e}")
