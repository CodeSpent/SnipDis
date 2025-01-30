import os
from bot import bot


def main():
    from dotenv import load_dotenv
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    try:
        bot.bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Error starting the bot: {e}")


if __name__ == "__main__":
    main()
