import os
from bot import bot
from bot.config import BOT_TOKEN

def main():


    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set!")

    try:
        bot.bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Error starting the bot: {e}")


if __name__ == "__main__":
    main()
