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
        applied_tags: List[discord.ForumTag] = None,
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

        # Combine all mentioned users for notifications
        all_mentioned_users = []
        if mention:
            all_mentioned_users.append(mention)
        if additional_mentions:
            all_mentioned_users.extend(additional_mentions)

        thread = await channel.create_thread(
            content=content_message,
            name=title.capitalize(),
            allowed_mentions=discord.AllowedMentions(users=all_mentioned_users) if all_mentioned_users else discord.AllowedMentions.none(),
            applied_tags=applied_tags if applied_tags else None
        )

        if thread:
            await thread.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(users=all_mentioned_users) if all_mentioned_users else discord.AllowedMentions.none()
            )

        """
        This is a hacky way of making sure that users who are mentioned get
        a proper notification & a thread indicator in their server list by
        creating a temporary comment in the new thread then deleting it.
        """
        if all_mentioned_users:
            mention_message = " ".join([user.mention for user in all_mentioned_users])
            temp_message = await thread.send(content=mention_message)
            await temp_message.delete()

        return thread
    except discord.HTTPException as e:
        raise Exception(f"Error creating thread: {str(e)}")
