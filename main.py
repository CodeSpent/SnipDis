import asyncio
from bot import bot
import sentry_sdk
import os



def main():
    """
    Entry point for starting the bot.
    """
    try:
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            send_default_pii=True,
        )

        asyncio.run(bot.run())
    except Exception as e:
        print(f"Error starting the bot: {e}")


if __name__ == "__main__":
    main()
