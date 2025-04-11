import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEV_GUILD_IDS = os.getenv("GUILD_IDS")
ENV = os.getenv("ENV", "PROD")