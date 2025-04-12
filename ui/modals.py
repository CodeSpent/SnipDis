import discord
from typing import List
import sentry_sdk
from bot.responder import Responder
from services.discord import create_forum_thread


class TitleInputModal(discord.ui.Modal):
    def __init__(
            self,
            ctx: discord.ApplicationContext,
            bot: discord.Bot,
            channel: discord.ForumChannel,
            url: str,
            message: str,
            tagged_users: List[discord.User]
    ):
        super().__init__(title="Provide a Title for the Post")

        self.title_input = discord.ui.InputText(
            label="Post Title:",
            style=discord.InputTextStyle.short,
            placeholder="Enter the title for your Forum post",
            max_length=100
        )

        self.add_item(self.title_input)

        self.ctx = ctx
        self.bot = bot
        self.channel = channel
        self.url = url
        self.tagged_users = tagged_users
        self.message = message

        self.responder = Responder()

    async def callback(self, interaction: discord.Interaction):
        self.responder.set_context(interaction)

        title = self.title_input.value
        if not title:
            await self.responder.error(
                "Title cannot be empty. Please submit a valid title."
            )
            return

        try:
            thread = await create_forum_thread(
                self.ctx,
                channel=self.channel,
                title=title,
                url=self.url,
                message=self.message,
                author=self.ctx.author,
                tagged_users=self.tagged_users
            )
            sentry_sdk.capture_message(
                f"Snip successfully created: {title}",
                level="info",
            )
            await self.responder.success(
                f"Thread **'{title}'** created successfully in {self.channel.mention}! \n\nView it [here]({thread.jump_url})."
            )
        except discord.Forbidden as forbidden_error:
            sentry_sdk.capture_exception(forbidden_error)
            await self.responder.error(
                "SnipDis lacks permissions to create threads in the selected Forum channel."
            )
        except Exception as general_error:
            sentry_sdk.capture_exception(general_error)
            await self.responder.error(
                f"An unexpected error occurred during thread creation: \n```\n{str(general_error)}```"
            )