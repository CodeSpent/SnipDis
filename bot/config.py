import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEV_GUILD_ID = os.getenv("GUILD_ID")
ENV = os.getenv("ENV", "PROD")