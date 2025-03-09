import os
import discord
from discord.ext import commands

import dotenv
import requests
from bs4 import BeautifulSoup

from bot.util import validate_and_normalize_url

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
intents = discord.Intents.default()

intents.guilds = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


def fetch_webpage_title(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        if soup.title and soup.title.string:
            return soup.title.string.strip()
        else:
            return None

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None



async def create_forum_thread(channel: discord.ForumChannel, title: str, url: str, author: discord.Member) -> discord.Thread:
    try:
        embed = discord.Embed(
            title=title,
            description="Here's some information about the provided link.",
            url=url,
            color=discord.Color.blue(),
        )

        embed.set_author(name=f"Requested by {author.display_name}",
                         icon_url=author.avatar.url if author.avatar else None)
        embed.add_field(name="Provided Link", value=url, inline=False)

        thread = await channel.create_thread(
            name=title,
            content=f"Here's the link: {url}"
        )
        await thread.send(embed=embed)
        return thread
    except discord.Forbidden:
        raise discord.Forbidden("Missing permissions to create threads in this channel.")
    except discord.HTTPException as e:
        raise Exception(f"Error creating thread: {str(e)}")


@bot.slash_command(description="Fetch a URL's title and post it in a forum channel as a thread.")
async def snip(ctx: discord.ApplicationContext, url: str, channel: discord.ForumChannel, title = None):
    url = validate_and_normalize_url(url)
    if not url:
        await ctx.respond("❌ The provided URL is invalid after validation! Ensure the URL is correct.", ephemeral=True)
        return

    try:
        if title is None:
            title = fetch_webpage_title(url)

        if title:
            thread = await create_forum_thread(channel, title, url, ctx.author)
            await ctx.respond(
                f"Thread **'{title}'** created successfully in {channel.mention}! View it [here]({thread.jump_url})."
            )
        else:
            await ctx.respond(
                "❌ Failed to extract title from page. \n Please provide the `title` argument manually."
            )

    except discord.Forbidden:
        await ctx.respond(
            "❌ The bot lacks permissions to create threads in the selected forum channel.", ephemeral=True
        )
    except Exception as e:
        await ctx.respond(
            f"❌ An unexpected error occurred: {str(e)}", ephemeral=True
        )


if __name__ == "__main__":
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"Failed to run bot: {e}")