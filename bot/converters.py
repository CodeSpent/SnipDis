from discord.ext import commands


class MentionsConverter(commands.Converter):
    async def convert(self, ctx, argument):
        mentions = argument.replace(",", " ").split()
        members = []

        for mention in mentions:
            try:
                if mention.startswith("<@") and mention.endswith(">"):
                    user_id = int(mention[2:-1].replace("!", ""))
                    user = await ctx.guild.fetch_member(user_id)
                else:
                    user = await commands.MemberConverter().convert(ctx, mention)

                members.append(user)
            except Exception as e:
                raise commands.BadArgument(f"Could not convert `{mention}` to a member.") from e