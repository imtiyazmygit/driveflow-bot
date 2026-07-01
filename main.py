import asyncio

from config import BROWSER_TYPE, DISCORD_WEBHOOK
from src.auth import start_now_and_login_with_browser_type
from src.booking_form import fill_initial_booking, load_centres
from src.slot_checker import booking_system_with_browser_rotation

# Discord webhook URL for sending booking notifications
discord_webhook = DISCORD_WEBHOOK


async def main():
    """Run the booking automation flow or exit gracefully when prerequisites are missing."""
    browser = None
    page = None
    playwright = None

    try:
        browser, _, page, playwright = await start_now_and_login_with_browser_type(BROWSER_TYPE)

        print("Current URL after login:", page.url)
        try:
            await page.wait_for_selector("form#slotSearchCommand", timeout=20000)
            print("Booking form detected")
        except Exception as e:
            print(f"Booking form not detected: {e}")
            html = await page.content()
            with open("debug_booking.html", "w", encoding="utf-8") as f:
                f.write(html)
            return

        centres = load_centres()
        if not centres:
            print("No centres found in centres.yaml or file missing")
            return

        first_centre = centres[0]
        print(f"Selected first centre: {first_centre}")

        try:
            await fill_initial_booking(page, first_centre)
            print(f"Booking form filled for {first_centre}")
        except Exception as e:
            print(f"Error while filling booking form: {e}")

        print("Starting complete booking process with rotation...")

        try:
            success = await booking_system_with_browser_rotation(
                page,
                centres,
                attempts_per_batch=100,
                break_minutes=3,
                discord_webhook=discord_webhook,
                max_bookings=3,
                initial_browser=BROWSER_TYPE,
            )

            if success:
                print("Booking process completed!")
            else:
                print("No bookings found in this cycle")

        except Exception as e:
            print(f"Error in booking process: {e}")

        print("Browser will remain open for manual review...")
        await asyncio.sleep(10)

    except RuntimeError as exc:
        print(f"Startup error: {exc}")
    except Exception as exc:
        print(f"Unexpected error: {exc}")
    finally:
        if browser is not None:
            try:
                await browser.close()
            except Exception:
                pass
        if playwright is not None:
            try:
                await playwright.stop()
            except Exception:
                pass


if __name__ == "__main__":
    asyncio.run(main())











