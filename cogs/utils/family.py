import discord
from discord.ext import commands

class Family():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if self.bot.user in message.mentions:
            if self.bot.db.family_is_member(message.author.id):
                await message.channel.send('ilybb')
            
    @commands.is_owner()
    @commands.command()
    async def addfamily(self, ctx, user_id: int):
        if not self.bot.db.family_is_member(user_id):
            self.bot.db.family_add(user_id)
            await ctx.channel.send(f'<@{user_id}> added to family. ♥')
            return
        await ctx.channel.send(f'Unable to add member or member already added.')