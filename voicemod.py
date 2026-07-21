import subprocess
import time
import pygetwindow as gw
import ctypes
import pyautogui
import pyperclip
from pathlib import Path

from utils.logger import logging
from config import (
    APP_PATH,
    APP_LAUNCH_DELAY,
    CLAIM,
    TRY_VOICE,
    MENU,
    ACTIVE_MENU,
    LOGIN,
)

def check_voicemod_installation():
    if Path(APP_PATH).exists():
        logging.info("Voicemod installation found.")
        return True

    logging.error(
        f"Voicemod not found at:\n\t\t\t\t  {APP_PATH}"
    )
    logging.error(
        "Please install Voicemod or update APP_PATH in config.py."
    )
    return False

def ensure_app_running():
    """Checks if Voicemod is running; spawns it if it isn't."""
    try:
        tasklist = subprocess.check_output(
            'tasklist /FI "IMAGENAME eq Voicemod.exe"', shell=True
        ).decode("utf-8", errors="ignore")
        if "Voicemod.exe" in tasklist:
            logging.info("Voicemod is already running. Skipping process creation.")
        else:
            logging.info("Voicemod is not running. Spawning new process...")
            subprocess.Popen([APP_PATH])
            logging.info("Voicemod started.")
            time.sleep(APP_LAUNCH_DELAY)
    except Exception as e:
        logging.error(f"Error checking or starting Voicemod: {e}")


def focus_voicemod_window():
    """Forces the Voicemod desktop application window to the foreground securely."""
    try:
        logging.info("Bringing Voicemod window to the foreground...")

        # Pull all windows containing "Voicemod"
        windows = gw.getWindowsWithTitle("Voicemod")
        voicemod_win = None

        for w in windows:
            title = w.title.strip()
            # Stricter check: Make sure it's the exact app window name
            # and ignore if it looks like a VS Code window or script file path
            if "Visual Studio Code" not in title and not title.endswith(
                (".py", ".json", ".txt")
            ):
                if (
                    title == "Voicemod"
                    or "Voicemod V3" in title
                    or title.startswith("Voicemod")
                ):
                    voicemod_win = w
                    break

        if voicemod_win:
            logging.info(f"Targeting exact window matching: '{voicemod_win.title}'")
            if voicemod_win.isMinimized:
                voicemod_win.restore()

            # Use Win32 API to securely force the target window forward
            hwnd = voicemod_win._hWnd
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # 9 = SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            time.sleep(1)
        else:
            logging.warning(
                "Could not find the distinct Voicemod app window. Fallback to general look up..."
            )
            # Emergency fallback if naming patterns mismatch completely
            if windows:
                windows[0].activate()
    except Exception as win_err:
        logging.warning(f"Failed to focus window automatically: {win_err}")


def hijack_browser_link(driver):
    """Intercepts the authentication link from the default browser window."""
    time.sleep(3)  # Wait for default browser to open the tab
    logging.info("Interacting with default browser to intercept the login link...")
    try:
        selenium_pid = driver.service.process.pid
    except Exception:
        selenium_pid = None

    default_browsers = ["Firefox", "Chrome", "Edge", "Browser"]
    browser_win = None

    for name in default_browsers:
        wins = gw.getWindowsWithTitle(name)
        for w in wins:
            if selenium_pid and getattr(w, "_pid", None) == selenium_pid:
                continue

            if "chromedriver" in w.title.lower() or "data:" in w.title.lower():
                continue

            browser_win = w
            break
        if browser_win:
            logging.info(f"Default browser: {browser_win}")
            break

    if browser_win:
        browser_win.activate()
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.6)
        pyautogui.hotkey("ctrl", "w")
        time.sleep(0.1)

        voicemod_login_url = pyperclip.paste()

        if (
            "voicemod.net" in voicemod_login_url
            or "account.voicemod" in voicemod_login_url
        ):
            logging.info(f"Successfully intercepted link: {voicemod_login_url}")
            try:
                logging.info("Attempting standard Selenium navigation...")
                driver.get(voicemod_login_url)
            except Exception as e:
                logging.warning(
                    f"Standard driver.get failed or timed out: {e}. Trying JavaScript execution fallback..."
                )
                driver.execute_script(f"window.location.href = '{voicemod_login_url}';")

            logging.info("Selenium session redirect executed.")
            time.sleep(5)
        else:
            logging.error("Failed to acquire valid Voicemod URL from clipboard.")
    else:
        logging.error("Could not locate the default browser window to hijack.")


def handle_app_initial_state():
    """Clears away initial transitions and popups to bring the app into a stable frame."""
    logging.info("Waiting for app state to settle (handling potential auto-login)...")
    time.sleep(2)

    logging.info("Sending 'esc' to dismiss any popup offers...")
    pyautogui.press("esc")
    time.sleep(2)


def trigger_claim():
    try:
        claim = pyautogui.locateOnScreen(CLAIM)
        if claim:
            logging.info("Claiming voice...")
            pyautogui.click(claim)
            try_voice = pyautogui.locateOnScreen(TRY_VOICE)
            if try_voice:
                pyautogui.click(try_voice)
            return True
        return False
    except pyautogui.ImageNotFoundException as e:
        logging.info(f"No Voice to Claim")
        return False


def find_menu(*images):
    for image in images:
        try:
            location = pyautogui.locateOnScreen(image)
            if location:
                return location
        except pyautogui.ImageNotFoundException:
            pass
    return None


def perform_app_logout(active=None):
    """Navigates through app UI to log out an active user session."""
    try:
        logging.info("Attempting to locate menu to log out existing account...")
        menu_dots = find_menu(MENU, ACTIVE_MENU)
        if menu_dots:
            logging.info("Clicking on menu to open the dropdown...")
            time.sleep(0.5)
            pyautogui.click(menu_dots)
            time.sleep(1)

            pyautogui.press("down")
            pyautogui.press("right")
            pyautogui.press("down")
            pyautogui.press("enter")

            logging.info("Successfully triggered Log out via keyboard menu navigation.")
            time.sleep(3)
            return True
    except Exception as e:
        logging.error(f"Error during logout sequence: {e}")
    return False


def trigger_app_login(driver):
    """Finds and clicks the landing login element, then intercepts its link handoff."""
    try:
        get_started = pyautogui.locateOnScreen(LOGIN)
        if get_started:
            logging.info("'Get Started' found. Clicking to proceed...")
            pyautogui.click(get_started)
            hijack_browser_link(driver)
            return True
        return False
    except pyautogui.ImageNotFoundException as e:
        logging.info(
            f"Login Section not detected. Assuming user is already logged in or no login required: {e}"
        )
        return False


def launch_voicemod_app(driver):
    try:
        ensure_app_running()
        focus_voicemod_window()
        handle_app_initial_state()

        logging.info("Checking final login state...")
        # If logged out, log in directly
        if trigger_app_login(driver):
            return True

        logging.info("User is already logged in. Proceeding to log out and re-login...")
        trigger_claim()
        # If not logged out, execute the logout sequence, then log in
        if perform_app_logout():
            trigger_app_login(driver)

        return True

    except Exception as e:
        logging.error(f"Error managing Voicemod desktop client application: {e}")
        return False
