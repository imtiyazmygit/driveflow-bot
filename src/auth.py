import asyncio
import os
import random
import subprocess
import time
from pathlib import Path

import yaml

try:
    from playwright.async_api import async_playwright
except Exception:  # pragma: no cover - handled at runtime
    async_playwright = None

try:
    from playwright_stealth import Stealth
except Exception:  # pragma: no cover - handled at runtime
    Stealth = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = os.getenv("DVSA_CONFIG_FILE", str(PROJECT_ROOT / "config.yaml"))

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
PROFILE_PATH = r"C:\chrome-profile"
PROFILE_PATH_2 = r"C:\edge-profile"


async def human_wait(min_sec=2, max_sec=5):
    """Simulate human-like delays between actions."""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


def load_config():
    """Load credentials from environment variables or a local YAML file."""
    env_user = os.getenv("DVSA_USERNAME") or os.getenv("GOVUK_USERNAME")
    env_password = os.getenv("DVSA_PASSWORD") or os.getenv("GOVUK_PASSWORD")

    if env_user and env_password:
        return {"credentials": {"user_id": env_user, "password": env_password}}

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if "credentials" in data:
            return data
        if "user_id" in data and "password" in data:
            return {"credentials": {"user_id": data["user_id"], "password": data["password"]}}

    return {}


def _browser_exists(path):
    return path and os.path.exists(path)


def resolve_browser_path(browser_type):
    if browser_type == "chrome":
        for path in CHROME_PATHS:
            if _browser_exists(path):
                return path
    elif browser_type == "edge":
        for path in EDGE_PATHS:
            if _browser_exists(path):
                return path
    return None


def launch_chrome():
    browser_path = resolve_browser_path("chrome")
    if not browser_path:
        raise FileNotFoundError("Chrome executable not found. Install Chrome or update the path in src/auth.py.")

    print("Launching Chrome with remote debugging...")
    cmd = [browser_path, "--remote-debugging-port=9222", f"--user-data-dir={PROFILE_PATH}"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)


def launch_edge():
    browser_path = resolve_browser_path("edge")
    if not browser_path:
        raise FileNotFoundError("Edge executable not found. Install Edge or update the path in src/auth.py.")

    print("Launching Edge with remote debugging...")
    cmd = [browser_path, "--remote-debugging-port=9223", f"--user-data-dir={PROFILE_PATH_2}"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)


async def handle_already_signed_in_page(page):
    """Handle the 'You are already signed in' page if it appears."""
    try:
        already_signed_in = await page.locator("h1:has-text('You are already signed in')").count()

        if already_signed_in > 0:
            print("Handling 'You are already signed in' page...")
            await page.click("input#confirm-Stay")
            print("Selected 'Stay signed in'")
            await page.click("button#continue")
            print("Clicked Continue")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            return True

        return False

    except Exception as e:
        print(f"Error handling signed in page: {e}")
        return False


async def start_now_and_login_with_browser_type(browser_type):
    """Launch a browser, authenticate, and open the booking form."""
    config = load_config()
    credentials = config.get("credentials", {})

    if not credentials.get("user_id") or not credentials.get("password"):
        raise RuntimeError(
            "Missing DVSA credentials. Set DVSA_USERNAME and DVSA_PASSWORD or create config.yaml."
        )

    if async_playwright is None:
        raise RuntimeError("Playwright is not installed. Run 'pip install -r requirements.txt'.")

    if browser_type not in {"chrome", "edge"}:
        raise ValueError("browser_type must be either 'chrome' or 'edge'")

    if browser_type == "chrome":
        launch_chrome()
        print("Connecting to launched Chrome...")
        port = 9222
    else:
        launch_edge()
        print("Connecting to launched Edge...")
        port = 9223

    try:
        if Stealth is not None:
            stealth = Stealth()
            p = await stealth.use_async(async_playwright()).__aenter__()
        else:
            p = await async_playwright().__aenter__()
        print("Connecting to launched browser...")

        browser = await p.chromium.connect_over_cdp(f"http://localhost:{port}")
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[-1] if context.pages else await context.new_page()

        await page.goto("https://www.gov.uk/book-pupil-driving-test")

        for y in range(0, 1500, 400):
            await page.mouse.wheel(0, y)
            await human_wait(1, 2)

        await page.wait_for_selector("a.govuk-button", timeout=15000)
        await human_wait(2, 4)
        await page.click("a.govuk-button")

        await page.wait_for_selector("input[name='user_id']", timeout=20000)

        user_value = await page.eval_on_selector("input[name='user_id']", "el => el.value")
        pass_value = await page.eval_on_selector("input[name='password']", "el => el.value")

        if not user_value.strip():
            print("Filling username...")
            await page.click("input[name='user_id']")
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
            for char in credentials["user_id"]:
                await page.type("input[name='user_id']", char, delay=random.randint(120, 280))
            await human_wait(1, 2)

        if not pass_value.strip():
            print("Filling password...")
            await page.click("input[name='password']")
            await page.keyboard.press("Control+a")
            await page.keyboard.press("Delete")
            for char in credentials["password"]:
                await page.type("input[name='password']", char, delay=random.randint(120, 280))
            await human_wait(1, 2)

        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")
        await human_wait(5, 8)

        print("Active URL after login:", page.url)

        print("Opening booking form in new tab...")
        booking_url = "https://driver-services.dvsa.gov.uk/obs-web/pages/home"
        new_page = await context.new_page()
        await new_page.goto(booking_url)
        await new_page.wait_for_load_state("domcontentloaded")

        await handle_already_signed_in_page(new_page)

        try:
            await new_page.wait_for_selector("form#slotSearchCommand", timeout=20000)
            print("Booking form detected in new tab")
        except Exception as e:
            print(f"Booking form not detected: {e}")

        return browser, context, new_page, p
    except Exception as exc:
        try:
            await p.stop()
        except Exception:
            pass
        raise RuntimeError(f"Failed to open the booking session: {exc}") from exc
