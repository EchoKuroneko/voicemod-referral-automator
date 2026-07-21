# Voicemod Referral Automator

Automates the Voicemod referral workflow by creating temporary email accounts, handling OTP verification, launching Voicemod, and cycling through referral claims. (WINDOWS ONLY SUPPORTED)

> [!WARNING]
> This project is intended for educational and automation purposes only. Users are responsible for complying with Voicemod's Terms of Service and any applicable policies.

---

## Features

- Automatic temporary email creation
- Automatic OTP retrieval
- Voicemod website automation using Selenium
- Voicemod desktop application automation
- Headless and visible browser modes
- Automatic cleanup of browser sessions
- Persistent `.env` configuration
- Logging support

---

## Installation

Clone the repository:

```bash
git clone https://github.com/EchoKuroneko/voicemod-referral-automator.git
cd voicemod-referral-automator
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file:

```env
LOGIN_URL=https://voicemod.net/friend/<invite_id>
```

You can find your invite link inside the Voicemod application.

If no `.env` file exists, the script will prompt you for your invite link on first launch and automatically save it.

### Custom Voicemod Installation Path

By default, the script expects Voicemod to be installed at:

```python
APP_PATH = r"C:\Program Files\Voicemod V3\Voicemod.exe"
```

If Voicemod is installed elsewhere, update `APP_PATH` in `config.py`.

Example:

```python
APP_PATH = r"D:\Programs\Voicemod\Voicemod.exe"
```

---

## Usage

Run:

```bash
python main.py
```

Example:

```python
run_cycles(
    iterations=5,
    headless=False
)
```

---

## Project Structure

```text
voicemod-referral-automator/
│
├── main.py
├── config.py
├── browser.py
├── mail_tm.py
├── web_login.py
├── voicemod.py
│
├── utils/
│   └── logger.py
│
├── assets/
│   ├── claim.png
│   ├── menu.png
│   ├── active_menu.png
│   └── ...
│
├── requirements.txt
├── .env
└── README.md
```

---

## Attribution

This project uses MailTM for temporary email functionality.

- MailTM API: https://mail.tm/
- Python library: https://github.com/olegbespalov/mailtm-python

Please review their respective licenses and usage policies before using this project.

---

## Disclaimer

This project is not affiliated with, endorsed by, or associated with Voicemod.

Voicemod is a trademark of its respective owners. Users are solely responsible for ensuring that their use of this software complies with Voicemod's Terms of Service and all applicable laws.

---

## License

MIT License