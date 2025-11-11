import discord
from discord import ApplicationContext, Interaction

from constants.messages import EMPTY_LINE_SYMBOL


class Responder:
    def __init__(self):
        """
        Initialize Responder with no context.
        The context needs to be set before sending a response.
        """
        self.ctx: ApplicationContext | Interaction | None = None

    def set_context(self, ctx: ApplicationContext | Interaction):
        """
        Set the context dynamically before using the Responder.

        Parameters:
            ctx (ApplicationContext | Interaction): The command context or interaction.
        """
        self.ctx = ctx

    def _ensure_context(self):
        """
        Ensure that the context is set before attempting a response.
        Raises an exception if `self.ctx` is None.
        """
        if not self.ctx:
            raise ValueError("Context is not set. Use 'set_context(ctx)' before calling this method.")

    async def _respond_with_embed(self, embed: discord.Embed, ephemeral: bool = True):
        """
        Send an embed response, handling both ApplicationContext and Interaction.

        Parameters:
            embed (discord.Embed): The embed to send.
            ephemeral (bool): Whether the message should be ephemeral (visible only to the user).
        """
        self._ensure_context()

        if isinstance(self.ctx, Interaction):
            await self.ctx.response.send_message(embed=embed, ephemeral=ephemeral)
        elif isinstance(self.ctx, ApplicationContext):
            await self.ctx.respond(embed=embed, ephemeral=ephemeral)
        else:
            raise ValueError("Unsupported context type. Only ApplicationContext and Interaction are supported.")

    async def respond(self, message: str, ephemeral: bool = True):
        """
        General-purpose response method to handle both ApplicationContext and Interaction.

        Parameters:
            message (str): The message to send to the user.
            ephemeral (bool): Whether the message should be ephemeral (visible only to the user).
        """
        self._ensure_context()

        message = EMPTY_LINE_SYMBOL + message

        if isinstance(self.ctx, Interaction):
            await self.ctx.response.send_message(message, ephemeral=ephemeral)
        elif isinstance(self.ctx, ApplicationContext):
            await self.ctx.respond(message, ephemeral=ephemeral)
        else:
            raise ValueError("Unsupported context type. Only ApplicationContext and Interaction are supported.")

    async def success(self, message: str):
        """
        Sends a success response with a green embed.

        Parameters:
            message (str): The message to send to the user.
        """
        embed = discord.Embed(description=message, color=discord.Color.green())
        await self._respond_with_embed(embed)

    async def error(self, message: str):
        """
        Sends an error response with a red embed.

        Parameters:
            message (str): The message to send to the user.
        """
        embed = discord.Embed(description=message, color=discord.Color.red())
        await self._respond_with_embed(embed)

    async def warning(self, message: str):
        """
        Sends a warning response with an orange embed.

        Parameters:
            message (str): The message to send to the user.
        """
        embed = discord.Embed(description=message, color=discord.Color.orange())
        await self._respond_with_embed(embed)

    async def clear(self, message: str):
        """
        Sends a response without formatting.

        Parameters:
            message (str): The message to send to the user.
        """
        await self.respond(message)