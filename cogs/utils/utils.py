import discord
from discord.ext import commands
from datetime import datetime
from time import time

class Utils:
    """base utilities for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.starttime = datetime.now()

    async def on_ready(self):
        print(f'Logged in as: {self.bot.user.name}')
        self.bot_log = self.bot.get_channel(508515073547960341)
        await self.bot_log.send(f'Starting up.. Running on {len(self.bot.guilds)} servers. Starttime: {self.bot.starttime}.')
        
    @commands.command()
    async def latency(self, ctx):
        await ctx.channel.send(f'Current Latency: {self.bot.latency:.2f}ms')

    @commands.command()
    async def ping(self, ctx):
        before = time()
        message = await ctx.channel.send('pong')
        ping = (time() - before) * 1000
        await message.edit(content=f'Current Ping: {ping:.2f}ms')

    @commands.command()
    async def uptime(self, ctx):
        ''': See how long I've been online'''
        time = datetime.now() - self.bot.starttime
        days = time.days
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await ctx.channel.send(f"I've been online for {days} days, {minutes} min, {seconds} seconds!")

    @commands.command()
    async def starttime(self, ctx):
        ''': See when I went online'''
        await ctx.channel.send(f'Running since: `{self.bot.starttime}`.')