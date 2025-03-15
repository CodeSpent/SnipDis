import asyncio
import os
import aiohttp
import discord
from typing import List, Optional
import dotenv
import requests
from bs4 import BeautifulSoup
from bot.util import validate_and_normalize_url, get_guild_ids_for_environment, truncate_string, fetch_proxies

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()

intents.guilds = True

bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    activity = discord.CustomActivity(type=discord.ActivityType.custom, name="Use /snip to snip the web!")

    await bot.change_presence(status=discord.Status.online, activity=activity)

    print("Syncing slash commands..")
    try:
        await bot.sync_commands()
        print("Commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


async def fetch_webpage_title(url: str) -> Optional[str]:
    """
    Fetches the title of a webpage using ScrapeOps API.

    :param url: The target webpage's URL.
    :param api_key: The API key for ScrapeOps.
    :return: The title of the webpage, or None if no title is found.
    """
    scrapeops_api_url = 'https://proxy.scrapeops.io/v1/'

    try:
        response = requests.get(
            url=scrapeops_api_url,
            params={
                'api_key': os.getenv('SCRAPEOPS_API_KEY'),
                'url': url,
            },
        )

        if response.status_code != 200:
            print(f"Failed to fetch the webpage, status code: {response.status_code}")
            return None

        html_content = response.content
        soup = BeautifulSoup(html_content, "html.parser")

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        twitter_title = soup.find("meta", property="twitter:title")
        if twitter_title and twitter_title.get("content"):
            return twitter_title["content"].strip()

        return None
    except Exception as e:
        print(f"An error occurred while fetching the webpage title: {e}")
        return None


async def create_forum_thread(
        channel: discord.ForumChannel,
        title: str,
        url: str,
        author: discord.User,
        tagged_users: List[discord.User]
) -> discord.Thread:
    try:
        embed = discord.Embed(
            title=title,
            url=url,
            color=discord.Color.green(),
        )

        embed.set_author(name=f"Snipped by {author.display_name}",
                         icon_url=author.avatar.url if author.avatar else None)
        embed.add_field(name="Provided Link", value=url, inline=False)

        if tagged_users:
            mentions = "\n".join(
                f"{user.mention} " for user in tagged_users
            )
            embed.add_field(name="Mentioned Users", value=mentions, inline=False)


        thread = await channel.create_thread(
            name=title,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(users=tagged_users)
        )

        if tagged_users:
            mention_message = " ".join([user.mention for user in tagged_users])
            temp_message = await thread.send(content=mention_message)
            await temp_message.delete()

        return thread
    except discord.Forbidden:
        raise discord.Forbidden("Missing permissions to create threads in this channel.")
    except discord.HTTPException as e:
        raise Exception(f"Error creating thread: {str(e)}")


@bot.slash_command(
    description="Snip a webpage & post it to a Forum channel",
    guild_ids=get_guild_ids_for_environment()
)
async def snip(
        ctx: discord.ApplicationContext,
        url: discord.Option(str, "The URL of the webpage to snip."),
        channel: discord.Option(discord.ForumChannel, "The Forum Channel to post to."),
        user: discord.Option(discord.User, "User to mention.", default=None, name="mention"),
        additional_users: discord.Option(str, "Additional user mentions (e.g. @user1 @user2)", default=None, name="mentions"),
        title: discord.Option(str, "Title of the post (default: Webpage's title).", default=None, min_length=1, max_length=100)
):
    await ctx.defer(ephemeral=True)

    url = validate_and_normalize_url(url)
    if not url:
        await ctx.respond("❌ The provided URL is invalid after validation! Ensure the URL is correct.", ephemeral=True)
        return

    tagged_users = []
    if user:
        tagged_users.append(user)

    if additional_users:
        user_mentions = additional_users.split(" ")
        for user_mention in user_mentions:
            user_id = user_mention.strip().strip("<@!>")
            try:
                fetched_user = await ctx.guild.fetch_member(int(user_id))
                if fetched_user:
                    tagged_users.append(fetched_user)
            except Exception:
                await ctx.respond(
                    f"⚠️ Unable to fetch one or more users from `additional_users`. Ensure you use valid mentions.",
                    ephemeral=True
                )
                return

    try:
        if not title:
            title = await fetch_webpage_title(url)

        if title:
            title = truncate_string(title[0].upper() + title[1:] if len(title) > 1 else title.upper())

        thread = await create_forum_thread(channel, title, url, ctx.author, tagged_users=tagged_users)

        await ctx.respond(
            f"Thread **'{title}'** created successfully in {channel.mention}! \n View it [here]({thread.jump_url}).",
            ephemeral=True
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