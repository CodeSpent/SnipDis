import asyncio
from bot import bot
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration

import os


def main():
    """
    Entry point for starting the bot.
    """
    try:
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            send_default_pii=True,
            debug=True,
            traces_sample_rate=1.0,
            integrations=[AsyncioIntegration()]
        )
        print("Sentry initialized successfully")
    except Exception as sentry_error:
        print(f"Sentry initialization failed: {sentry_error}")

    # This is to healthcheck Sentry reporting
    # on initialization. There have been some
    # issues when spinning up the instance
    # where reporting times out as it comes
    # back online which creates a lapse in
    # reporting. This ensures that there's no
    # downtime when reinitializing.
    #
    # We should find a more appropriate solution
    # but this works for now.
    try:
        raise ValueError("Test error for Sentry")
    except ValueError as e:
        sentry_sdk.capture_exception(e)

    try:
        asyncio.run(bot.run())
    except Exception as e:
        print(f"Error starting the bot: {e}")


if __name__ == "__main__":
    main()
