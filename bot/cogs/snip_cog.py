import discord
from discord.ext import commands

from services.discord import create_forum_thread
from ui.modals import TitleInputModal
from bot.util import (
    fetch_webpage_title,
    validate_and_normalize_url,
    fetch_youtube_video_title,
    get_domain_from_url
)


class SnipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="snip",
        description="Snip a webpage & post it to a Forum channel"
    )
    async def snip(
            self,
            ctx: discord.ApplicationContext,
            url: discord.Option(str, "The URL of the webpage to snip."),
            channel: discord.Option(discord.ForumChannel, "The Forum Channel to post to."),
            user: discord.Option(discord.User, "User to mention.", default=None, name="mention"),
            additional_users: discord.Option(str, "Additional user mentions (e.g., @user1 @user2)", default=None,
                                             name="mentions"),
            title: discord.Option(str, "Title of the post (default: Webpage's title).", default=None, min_length=1,
                                  max_length=100)
    ):
        url = validate_and_normalize_url(url)
        if not url:
            await ctx.respond("🔴 Error!\n\nThe provided URL is invalid after validation! Ensure the URL is correct.",
                              ephemeral=True)
            return

        if not title:
            domain = get_domain_from_url(url)
            if domain in ["youtube.com", "youtu.be"]:
                title = await fetch_youtube_video_title(url)
                if not title:
                    await ctx.respond("🔴 Error!\n\nCouldn't fetch the title for this YouTube video.", ephemeral=True)
                    return
            else:
                title = await fetch_webpage_title(url)
                if not title:
                    modal = TitleInputModal(ctx, self.bot, channel=channel, url=url, tagged_users=[])
                    await ctx.send_modal(modal)
                    return

        await ctx.defer(ephemeral=True)

        tagged_users = []
        if user:
            tagged_users.append(user)

        if additional_users:
            user_mentions = additional_users.split(" ")
            for user_mention in user_mentions:
                user_id = user_mention.strip().strip("<@!>")  # Remove mention formatting
                try:
                    fetched_user = await ctx.guild.fetch_member(int(user_id))
                    if fetched_user:
                        tagged_users.append(fetched_user)
                except Exception:
                    await ctx.respond(
                        "⚠️ Unable to fetch one or more users from `additional_users`. Ensure you use valid mentions.",
                        ephemeral=True
                    )
                    return

        try:
            thread = await create_forum_thread(ctx, channel, title, url, ctx.author, tagged_users)
            await ctx.respond(
                f"🟢 Success!\n\nThread **'{title}'** created successfully in {channel.mention}! \n\nView it [here]({thread.jump_url}).",
                ephemeral=True
            )
        except discord.Forbidden:
            await ctx.respond(
                "🔴 Error!\n\nThe bot lacks permissions to create threads in the selected forum channel.", ephemeral=True
            )
        except Exception as e:
            await ctx.respond(
                f"🔴 Error!\n\nAn unexpected error occurred: {str(e)}", ephemeral=True
            )


def setup(bot):
    bot.add_cog(SnipCog(bot))
