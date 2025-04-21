from discord import ApplicationContext, Interaction

from constants.messages import EMPTY_LINE_SYMBOL, SUCCESS_EMOJI, FAILURE_EMOJI, WARNING_EMOJI


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
        Sends a success response with the Success icon.

        Parameters:
            message (str): The message to send to the user.
        """
        await self.respond(f"{SUCCESS_EMOJI} {message}")

    async def error(self, message: str):
        """
        Sends an error response with the Failure icon.

        Parameters:
            message (str): The message to send to the user.
        """
        await self.respond(f"{FAILURE_EMOJI} {message}")

    async def warning(self, message: str):
        """
        Sends a warning response with the Warning icon.

        Parameters:
            message (str): The message to send to the user.
        """
        await self.respond(f"⚠{WARNING_EMOJI} {message}")

    async def clear(self, message: str):
        """
        Sends a response without formatting.

        Parameters:
            message (str): The message to send to the user.
        """
        await self.respond(message)