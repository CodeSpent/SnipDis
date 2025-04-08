import discord
from discord.ext import commands
from discord import ApplicationContext, Option, PermissionOverwrite, CategoryChannel, Role, Guild
from bot.responder import Responder


class ForumsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.responder = Responder()

    @commands.slash_command(
        name="forum",
        description="Create a new forum channel for your Snips."
    )
    async def create_forum(
            self,
            ctx: ApplicationContext,
            name: Option(str, "The name of the Forum channel."),
            description: Option(str, "A short description for the Forum channel."),
            category: Option(discord.CategoryChannel, "The category to create the Forum channel in.", required=False),
            roles: Option(str, "Comma-separated role names to allow access.", required=False)
    ):
        self.responder.set_context(ctx)

        if not ctx.author.guild_permissions.manage_channels:
            await self.responder.error("You do not have permission to create a forum channel.")
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
            forum_channel: discord.ForumChannel = await guild.create_forum_channel(
                name=name,
                topic=description[:1024],  # Discord limits to 1024 characters
                overwrites=overwrites,
                category=category
            )

            await self.responder.success(
                f"Successfully created forum channel [`{forum_channel.name}`]({forum_channel.jump_url})."
            )
        except discord.Forbidden:
            await self.responder.error("Missing permissions to create channels.")
        except Exception as e:
            await self.responder.error(f"An unexpected error occurred: {e}")

    @commands.slash_command(
        name="category",
        description="Create a new category for your Snips Forum"
    )
    async def create_category(
            self,
            ctx: ApplicationContext,
            name: Option(str, "The name of the category."),
            roles: Option(str, "Comma-separated role names to allow access.", required=False),
            position: Option(int, "Position of the category (order in the channel list).", required=False),
            nsfw: Option(bool, "Mark the category as NSFW (Not Safe For Work)", default=False)
    ):
        self.responder.set_context(ctx)

        if not ctx.author.guild_permissions.manage_channels:
            await self.responder.error("You do not have permission to create a category.")
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
            # Create the category with the specified options
            category_channel: CategoryChannel = await guild.create_category_channel(
                name=name,
                overwrites=overwrites,
                position=position,
                nsfw=nsfw
            )

            await self.responder.success(
                f"Successfully created category [`{category_channel.name}`]({category_channel.jump_url})."
            )
        except discord.Forbidden:
            await self.responder.error("Missing permissions to create channels.")
        except Exception as e:
            await self.responder.error(f"An unexpected error occurred: {e}")


def setup(bot):
    bot.add_cog(ForumsCog(bot))