import os

# Browser configuration
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chrome").lower()

# Optional Discord notifications
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")