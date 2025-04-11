from discord.ext import commands
from discord import slash_command, Option, Guild, ForumChannel, CategoryChannel, PermissionOverwrite, Role
import discord

from bot.responder import Responder


class SetupCog(commands.Cog):
    @slash_command(
        name="startforum",
        description="Create a full category and channel setup in one command."
    )
    async def setup(
            self,
            ctx: discord.ApplicationContext,
            name: Option(str, "The name of the Forum channel to create."),
            description: Option(str, "A  description for the Forum channel."),
            category: Option(discord.CategoryChannel, "The category to create the Forum channel in.", required=False),
            category_name: Option(str, "The name of the category to create for your Forum channel.", required=False),
            nsfw_category: Option(bool, "Mark the category as NSFW (Not Safe For Work).", default=False),
            roles: Option(str, "Comma-separated role names to allow access.", required=False),
            position: Option(int, "Position of the category in the list.", required=False)
    ):
        self.responder.set_context(ctx)

        if position is not None and category is not None:
            await self.responder.error("You cannot modify the position of an existing category.")
            return

        if not ctx.author.guild_permissions.manage_channels:
            await self.responder.error("You do not have permission to use this command.")
            return

        await ctx.defer(ephemeral=True)

        guild: Guild = ctx.guild

        if not guild:
            await self.responder.error("Could not find server with provided id.")
            return

        role_objects = []
        if roles:
            role_names = [role_name.strip() for role_name in roles.split(",")]
            for role_name in role_names:
                role: Role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    role_objects.append(role)
                else:
                    await self.responder.warning(f"Role `{role_name}` not found. This role will be ignored.")

        overwrites = {
            guild.default_role: PermissionOverwrite(view_channel=False),
        }
        for role in role_objects:
            overwrites[role] = PermissionOverwrite(view_channel=True)

        try:
            category: CategoryChannel = await guild.create_category_channel(
                name=category_name,
                overwrites=overwrites,
                position=position
            )

            forum_channel: ForumChannel = await guild.create_forum_channel(
                name=name,
                topic=description[:1024],
                overwrites=overwrites,
                nsfw=nsfw_category,
                category=category
            )

            await self.responder.success(
                f"""Successfully created:
                - Category: [`{category.name}`]
                - Forum Channel: [`{forum_channel.name}`]({forum_channel.jump_url})
                """
            )

        except discord.Forbidden:
            await self.responder.error("Missing permissions to create channels.")
        except Exception as e:
            await self.responder.error(f"An unexpected error occurred: {e}")

    def __init__(self, bot):
        self.bot = bot
        self.responder = Responder()


def setup(bot):
    bot.add_cog(SetupCog(bot))
