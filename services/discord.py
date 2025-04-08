import discord
from typing import List

from discohook.command import message


async def create_forum_thread(
        ctx: discord.ApplicationContext,
        channel: discord.ForumChannel = None,
        title: str = None,
        url: str = None,
        author: discord.User = None,
        tagged_users: List[discord.User] = None,
        message: str = None,
) -> discord.Thread:
    if title is None:
        # TODO: We shouldn't respond here
        await ctx.respond(
            "❓ The webpage title could not be fetched from the URL. Please provide a title for the post:",
            ephemeral=True
        )

    try:
        embed = discord.Embed(
            title=title,
            url=url,
            color=discord.Color.green(),
        )
        embed.set_author(name=f"Snipped by {author.display_name}",
                         icon_url=author.avatar.url if author.avatar else None)
        embed.add_field(name="Snipped Link", value=url, inline=True)
        embed.set_footer(text=f"Snipped by {author.display_name}")



        if tagged_users:
            mentions = "\n".join(
                f"{user.mention} " for user in tagged_users
            )
            embed.add_field(name="Mentioned Users", value=mentions, inline=False)

        if message is None:
            message = ""

        content_message = f"**\n{author}** snipped **{title.capitalize()}.**\n\n {message}\n\nLink:\n{url}\n\nSnipped by:\n {author.mention}"

        thread = await channel.create_thread(
            content=content_message,
            name=title.capitalize(),
            allowed_mentions=discord.AllowedMentions(users=tagged_users)
        )

        if thread:
            await thread.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(users=tagged_users)
            )

        if tagged_users:
            mention_message = " ".join([user.mention for user in tagged_users])
            temp_message = await thread.send(content=mention_message)
            await temp_message.delete()

        return thread
    except discord.HTTPException as e:
        raise Exception(f"Error creating thread: {str(e)}")
