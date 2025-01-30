import os

import discord

from bot import bot
import discohook

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
APP_ID = os.getenv("APP_ID")
APP_PW = os.getenv("APP_PW")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

app = discohook.Client(
    application_id=APP_ID,
    public_key=PUBLIC_KEY,
    token=BOT_TOKEN,
    password=APP_PW,
    default_help_command=True
)

@app.on_error()
async def handler(_request, err: Exception):
    await app.send("", f"Error: {err}")

@app.load
@discohook.command.slash(name="Snip", description="Snip snip")
async def snip(i: discohook.Interaction, url: str, channel: discord.ForumChannel):
    await i.response.send(url)
