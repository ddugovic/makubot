import discord
from discord.ext import commands


class Family(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            if message.author.bot:
                return
            ctx = await self.bot.get_context(message)
            if ctx.command:
                return  # do not trigger if there is another command processed

            if self.bot.db.family_is_member(message.author.id):
                if any(c in message.content.lower() for c in ("ily", "i love you")):
                    await message.channel.send(
                        f"I love you too <@{message.author.id}> ♥"
                    )
                else:
                    await message.channel.send(f"I love you <@{message.author.id}> ♥")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def addfamily(self, ctx, user_id: int):
        if not self.bot.db.family_is_member(user_id):
            self.bot.db.family_add(user_id)
            await ctx.channel.send(f"<@{user_id}> added to family. ♥")
            return
        await ctx.channel.send(f"Unable to add member or member already added.")


def setup(bot):
    bot.add_cog(Family(bot))
