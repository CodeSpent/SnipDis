import discord
from typing import List

from bot.util import build_mentioned_users_string
from constants.messages import EMPTY_LINE_SYMBOL


async def create_forum_thread(
        channel: discord.ForumChannel = None,
        title: str = None,
        url: str = None,
        mention: discord.User = None,
        author: discord.User = None,
        additional_mentions: List[discord.User] = None,
        message: str = "",
) -> discord.Thread:
    try:
        embed = discord.Embed(
            title=title,
            url=url,
            color=discord.Color.green(),
        )
        embed.set_author(name=f"Snipped by {author.display_name}", icon_url=author.avatar.url if author.avatar else None)
        embed.add_field(name="Snipped Link", value=url, inline=True)
        embed.set_footer(text=f"Snipped by {author.display_name}")

        if mention:
            mentions = build_mentioned_users_string(mention, additional_mentions)
            embed.add_field(name="Mentions", value=mentions, inline=False)

        def _construct_message():
            parts = [
                EMPTY_LINE_SYMBOL,
                f"**{title.capitalize()}**",
                f"{message}" if message else "",
                f"Snipped URL:\n{url}",
                f"Snipped by:\n{author.mention}",
            ]

            return "\n\n".join(filter(bool, parts))

        content_message = _construct_message()

        thread = await channel.create_thread(
            content=content_message,
            name=title.capitalize(),
            allowed_mentions=discord.AllowedMentions(users=additional_mentions)
        )

        if thread:
            await thread.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(users=additional_mentions)
            )

        """
        This is a hacky way of making sure that users who are mentioned get
        a proper notification & a thread indicator in their server list by
        creating a temporary comment in the new thread then deleting it.
        """
        if additional_mentions:
            mention_message = " ".join([user.mention for user in additional_mentions])
            temp_message = await thread.send(content=mention_message)
            await temp_message.delete()

        return thread
    except discord.HTTPException as e:
        raise Exception(f"Error creating thread: {str(e)}")
