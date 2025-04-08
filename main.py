import asyncio
from bot import bot

def main():
    """
    Entry point for starting the bot.
    """
    try:
        asyncio.run(bot.run())
    except Exception as e:
        print(f"Error starting the bot: {e}")


if __name__ == "__main__":
    main()
