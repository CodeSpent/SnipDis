import discord
import sentry_sdk
from discord.ext import commands
from bot.responder import Responder
from bot.util import (
    fetch_webpage_title,
    validate_and_normalize_url,
    fetch_youtube_video_title,
    get_domain_from_url,
    convert_string_id_to_discord_member
)
from services.discord import create_forum_thread
from ui.modals import TitleInputModal


class SnipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.responder = Responder()

    async def tag_autocomplete(self, ctx: discord.AutocompleteContext):
        """
        Autocomplete function for forum tags.
        Returns available tags from the selected forum channel.
        """
        # Get the forum channel from the current interaction options
        channel_id_or_obj = ctx.options.get("channel")

        if not channel_id_or_obj:
            # User hasn't selected a channel yet - provide a helpful message
            return [discord.OptionChoice(name="⚠️ Please select a channel first", value="")]

        # If channel is a string (ID), we need to fetch the actual channel object
        if isinstance(channel_id_or_obj, str):
            try:
                channel_id = int(channel_id_or_obj)
                channel = ctx.bot.get_channel(channel_id)

                if not channel:
                    # Try fetching from API if not in cache
                    channel = await ctx.bot.fetch_channel(channel_id)

            except (ValueError, discord.HTTPException) as e:
                sentry_sdk.add_breadcrumb(
                    category="tag_autocomplete",
                    message="Failed to resolve channel from ID",
                    data={
                        "channel_id": channel_id_or_obj,
                        "error": str(e)
                    },
                    level="error"
                )
                return [discord.OptionChoice(name="⚠️ Could not fetch channel", value="")]
        else:
            channel = channel_id_or_obj

        # Check if channel has available_tags attribute (forum-specific)
        if not hasattr(channel, 'available_tags'):
            return [discord.OptionChoice(name="⚠️ Selected channel is not a forum", value="")]

        # Check if the forum has any tags configured
        if not channel.available_tags:
            return [discord.OptionChoice(name="⚠️ This forum has no tags configured", value="")]

        # Get current user input
        current_input = ctx.value.lower() if ctx.value else ""

        # Filter and return matching tags
        choices = []
        for tag in channel.available_tags:
            if current_input in tag.name.lower():
                choices.append(discord.OptionChoice(name=tag.name, value=tag.name))

        # If no tags match the input, show a helpful message
        if not choices and current_input:
            return [discord.OptionChoice(name=f"⚠️ No tags match '{current_input}'", value="")]

        # Discord limits autocomplete to 25 choices
        return choices[:25]

    @discord.slash_command(
        name="snip",
        description="Snip a webpage & post it to a Forum channel"
    )
    async def snip(
            self,
            ctx: discord.ApplicationContext,
            url: discord.Option(str, "The URL of the webpage to snip."),
            channel: discord.Option(discord.ForumChannel, "The Forum Channel to post to."),
            title: discord.Option(str, "Title of the post (default: Webpage's title).", default=None, min_length=1, max_length=100),
            message: discord.Option(str, "Message body for the Snip.", default=None, min_length=1, max_length=1000),
            mention: discord.Option(discord.User, "User to mention.", default=None, name="mention"),
            additional_mentions: discord.Option(str, "Additional user mentions (e.g., @user1 @user2)", default="", name="mentions"),
            tags: discord.Option(str, "Tags to apply (comma-separated)", default=None, autocomplete=tag_autocomplete),
    ):
        sentry_sdk.add_breadcrumb(
            category="snip",
            message=f"Snip command invocation by {ctx.author.name}#{ctx.author.discriminator}",
            data={
                "url": url,
                "channel": {
                    "id": channel.id,
                    "name": channel.name
                },
                "title": title,
                "additional_users": additional_mentions,
                "mentioned_user": mention.name if mention else None,
                "message": message,
                "tags": tags,
                "issuer": {
                    "id": ctx.author.id,
                    "name": ctx.author.name,
                    "discriminator": ctx.author.discriminator
                }
            },
            level="info"
        )

        self.responder.set_context(ctx)

        # Mark the original url for telemetry
        original_url = url
        url = validate_and_normalize_url(url)

        if not url:
            await self.responder.error("The provided URL is invalid after validation! Ensure the URL is correct.")
            sentry_sdk.add_breadcrumb(
                category="snip",
                message="Invalid URL after validation",
                data={"url": url},
                level="error"
            )
            return

        sentry_sdk.add_breadcrumb(
            category="snip",
            message="URL validated",
            data={
                "original_url": original_url,
                "validated_url": url
            },
            level="info"
        )

        async def _invoke_title_modal(ctx: discord.ApplicationContext):
            """
            Sentry breadcrumb needs to be initialized before invoking modal
            to avoid losing scoped context up to here causing any requests
            with modal invocation to be completely ignored in Sentry.

            new_scope() lets us push this context, but this will not work
            anywhere other than this point in time.
            """
            sentry_sdk.add_breadcrumb(
                category="snip",
                message="Invoking TitleInputModal due to missing title",
                data={"url": url},
                level="info"
            )

            with sentry_sdk.new_scope() as scope:
                scope.set_context("modal_invocation", {
                    "user": ctx.author.name,
                    "user_id": ctx.author.id,
                    "guild": str(ctx.guild),
                    "channel": str(ctx.channel),
                    "url": url,
                    "action": "title_modal_invocation"
                })

                modal = TitleInputModal(
                    ctx=ctx,
                    bot=self.bot,
                    channel=channel,
                    url=url,
                    message=message,
                    mention=mention,
                    additional_mentions=additional_mentions,
                    applied_tags=applied_tags
                )

                modal.sentry_context = {
                    "user": ctx.author.name,
                    "user_id": ctx.author.id,
                    "url": url
                }

                await ctx.send_modal(modal)

        additional_mentions = [convert_string_id_to_discord_member(ctx, user_id) for user_id in additional_mentions.split()]

        # Parse and validate tags
        applied_tags = []
        if tags:
            # Split comma-separated tag names
            tag_names = [tag.strip() for tag in tags.split(',') if tag.strip()]

            # Match tag names to actual ForumTag objects
            for tag_name in tag_names:
                matching_tag = next((tag for tag in channel.available_tags if tag.name == tag_name), None)
                if matching_tag:
                    applied_tags.append(matching_tag)

            sentry_sdk.add_breadcrumb(
                category="snip",
                message="Tags parsed and validated",
                data={
                    "requested_tags": tag_names,
                    "applied_tags": [tag.name for tag in applied_tags]
                },
                level="info"
            )

        if not title:
            domain = get_domain_from_url(url)
            sentry_sdk.add_breadcrumb(
                category="snip",
                message="Extracted domain from URL",
                data={
                    "domain": domain,
                    "url": url
                },
                level="info"
            )

            if domain in ["youtube.com", "youtu.be"]:
                title = await fetch_youtube_video_title(url)
                if not title:
                    sentry_sdk.add_breadcrumb(
                        category="snip",
                        message="Failed to fetch YouTube video title; invoking modal",
                        data={"url": url, "domain": domain},
                        level="warning"
                    )
                    await _invoke_title_modal(ctx)
                    return
            else:
                title = await fetch_webpage_title(url)
                if not title:
                    sentry_sdk.add_breadcrumb(
                        category="snip",
                        message="Failed to fetch webpage title; invoking modal",
                        data={"url": url, "domain": domain},
                        level="warning"
                    )
                    await _invoke_title_modal(ctx)
                    return

        sentry_sdk.add_breadcrumb(
            category="snip",
            message="Title determined successfully",
            data={"title": title, "url": url},
            level="info"
        )

        await ctx.defer(ephemeral=True)

        tagged_users = []
        if mention:
            tagged_users.append(mention)
        if additional_mentions:
            tagged_users.extend(additional_mentions)

        sentry_sdk.add_breadcrumb(
            category="snip",
            message="User mentions processed",
            data={"tagged_users": [user.name for user in tagged_users if user]},
            level="info"
        )

        try:
            thread = await create_forum_thread(
                channel=channel,
                title=title,
                url=url,
                message=message,
                author=ctx.author,
                mention=mention,
                additional_mentions=additional_mentions,
                applied_tags=applied_tags if applied_tags else None
            )
            sentry_sdk.add_breadcrumb(
                category="snip",
                message="Snip thread created successfully",
                data={
                    "title": title,
                    "url": url,
                    "channel": channel.name,
                    "thread_url": thread.jump_url
                },
                level="info"
            )
            await self.responder.success(
                f"Thread **'{title}'** successfully created in {channel.mention}! \n\nView it [here]({thread.jump_url})."
            )

            sentry_sdk.capture_message(
                f"Snip successfully created: {title}",
                level="info",
            )
            return
        except discord.Forbidden:
            sentry_sdk.capture_message(
                f"Failed to create Snip: Missing permissions in {channel.name}",
                level="error"
            )
            await self.responder.error(
                "SnipDis lacks permissions to create threads in the selected forum channel."
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            await self.responder.error(
                f"An unexpected error occurred: {str(e)}"
            )


def setup(bot):
    bot.add_cog(SnipCog(bot))
