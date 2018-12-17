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
        _uptime = datetime.now() - self.bot.starttime
        await ctx.channel.send(f'I\'ve been online for `{_uptime}`.')

    @commands.command()
    async def starttime(self, ctx):
        ''': See when I went online'''
        await ctx.channel.send(f'Running since: `{self.bot.starttime}`.')

    @commands.command()
    async def servertime(self, ctx):
        ''': See what my current time is'''
        await ctx.channel.send(f'Current Servertime: `{datetime.now()}`.')
    
    @commands.command()
    async def serverinfo(self, ctx):
        ''': Show info to current server'''
        region = ctx.guild.region
        name = ctx.guild.name
        icon_url = ctx.guild.icon_url
        owner = ctx.guild.owner
        text_channels = ctx.guild.text_channels
        voice_channels = ctx.guild.voice_channels
        members = ctx.guild.members

        embed = discord.Embed(title=name, description=f'Server Information', color=discord.Color(0xff8eed))
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text=f'Server ID <{ctx.guild.id}>')
        embed.add_field(name='Owner', value=f'{owner}')
        embed.add_field(name='Users', value=f'{len(members)} ({len([member for member in members if member.status is not discord.Status.offline])} online)')
        embed.add_field(name='Text Channels', value=f'{len(text_channels)}')
        embed.add_field(name='Voice Channels', value=f'{len(voice_channels)}')
        embed.add_field(name='Region', value=f'{region}')
        await ctx.channel.send(embed=embed)