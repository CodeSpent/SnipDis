from discord import ApplicationContext


class Responder:
    def __init__(self):
        """
        Initialize Responder with no context.
        The context needs to be set before sending a response.
        """
        self.ctx: ApplicationContext | None = None

    def set_context(self, ctx: ApplicationContext):
        """
        Set the context dynamically before using the Responder.

        Parameters:
            ctx (discord.ApplicationContext): The command context.
        """
        self.ctx = ctx

    def _ensure_context(self):
        """
        Ensure that the context is set before attempting a response.
        Raises an exception if `self.ctx` is None.
        """
        if not self.ctx:
            raise ValueError("Context is not set. Use 'set_context(ctx)' before calling this method.")

    async def success(self, message: str):
        """
        Sends a success response with the ✅ icon.

        Parameters:
            message (str): The message to send to the user.
        """
        self._ensure_context()
        await self.ctx.respond(f"✅ {message}", ephemeral=True)

    async def error(self, message: str):
        """
        Sends an error response with the 🔴 icon.

        Parameters:
            message (str): The message to send to the user.
        """
        self._ensure_context()
        await self.ctx.respond(f"🔴 {message}", ephemeral=True)

    async def warning(self, message: str):
        """
        Sends a warning response with the ⚠️ icon.

        Parameters:
            message (str): The message to send to the user.
        """
        self._ensure_context()
        await self.ctx.respond(f"⚠️ {message}", ephemeral=True)

    async def info(self, message: str):
        """
        Sends an informational response with the ℹ️ icon.

        Parameters:
            message (str): The message to send to the user.
        """
        self._ensure_context()
        await self.ctx.respond(f"ℹ️ {message}", ephemeral=True)

    async def clear(self, message: str):
        """
        Sends a response without formatting as is.
        
        Parameters:
            message (str): The message to send to the user.
        """
        self._ensure_context()
        await self.ctx.respond(message, ephemeral=True)
