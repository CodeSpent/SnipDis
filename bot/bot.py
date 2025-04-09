import os
import discord
from dotenv import load_dotenv
from .util import get_guild_ids_for_environment

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    """
    Event triggered when the bot becomes ready to use.
    It performs actions like syncing slash commands and setting the bot status.
    """
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    activity = discord.CustomActivity(type=discord.ActivityType.custom, name="Use /snip to snip the web!")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    print("Syncing slash commands...")
    try:
        await bot.sync_commands(commands=bot.application_commands, guild_ids=get_guild_ids_for_environment())
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def load_cogs():
    """
    Dynamically load all cogs (command extensions) in the 'bot/cogs' directory.
    """
    cogs_directory = "bot/cogs"
    for filename in os.listdir(cogs_directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"{cogs_directory.replace('/', '.')}.{filename[:-3]}"  # Convert to import path
            try:
                bot.load_extension(cog_name)
                print(f"Loaded {cog_name} successfully.")
            except Exception as e:
                print(f"Failed to load {cog_name}: {e}")



async def run():
    """
    Asynchronous entry point to start the bot and load commands.
    """
    async with bot:
        await load_cogs()
        await bot.start(BOT_TOKEN)
