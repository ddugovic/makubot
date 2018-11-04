import discord
from discord.ext import commands
from utils import Config

class Settings():
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def prefix(self, ctx, prefix: str):
        try:
            Config.set_prefix(prefix)
        except ValueError:
            await ctx.channel.send(f'Prefix invalid or not all Values set properly.')
        
        await ctx.channel.send(f'Prefix changed to `{prefix}`')