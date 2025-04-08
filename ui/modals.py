import discord
from typing import List
from services.discord import create_forum_thread

class TitleInputModal(discord.ui.Modal):
    def __init__(self, ctx: discord.ApplicationContext, bot: discord.Bot, channel: discord.ForumChannel, url: str,
                 tagged_users: List[discord.User]):
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

    async def callback(self, interaction: discord.Interaction):
        title = self.title_input.value
        if not title:
            await interaction.response.send_message(
                "⚠️ Title cannot be empty. Please try submitting a valid title.",
                ephemeral=True
            )
            return

        try:
            thread = await create_forum_thread(
                self.ctx, self.channel, title, self.url, self.ctx.author, self.tagged_users
            )
            await interaction.response.send_message(
                f"🟢 Success!\n\nThread **'{title}'** created successfully in {self.channel.mention}! \n\nView it [here]({thread.jump_url}).",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "🔴 Error!\n\nThe bot lacks permissions to create threads in the selected Forum channel.", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"🔴 Error!\n\n An unexpected error occurred during thread creation: \n```\n{str(e)}```", ephemeral=True
            )
