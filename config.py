from selenium.webdriver.common.by import By

# Update this if Voicemod is installed in a different location.
APP_PATH = r"C:\Program Files\Voicemod V3\Voicemod.exe"

WAIT_TIMEOUT = 30
APP_LAUNCH_DELAY = 15
CHROME_VERSION = 150

BASE_URL = "https://account.voicemod.net"

DOWNLOAD_BUTTON = (By.XPATH, "//a[normalize-space()='Download for Free']")

EMAIL_INPUT = (By.ID, "email-login-email")
CONTINUE_BUTTON = (By.CLASS_NAME, "email-login__submit-button")
CHECKBOX_LABEL = (By.XPATH, "//span[contains(text(),'Verify you are human')]/..")
CHECKBOX = (By.XPATH, "./input[@type='checkbox']")

OTP_INPUTS = [(By.ID, f"inputBox{i}") for i in range(6)]
VERIFY_BUTTON = (By.CLASS_NAME, "input-email-code__verify-button")

CLAIM = r"assets\claim.png"
TRY_VOICE = r"assets\try_this_voice.png"
MENU = r"assets\menu_dots.png"
ACTIVE_MENU = r"assets\active_menu_dots.png"
LOGIN = r"assets\get_started_btn.png"
