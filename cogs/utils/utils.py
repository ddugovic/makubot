import discord
from discord.ext import commands
from datetime import datetime, timedelta
from time import time

class Utils:
    """base utilities for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.starttime = datetime.now().replace(microsecond=0)

    async def on_ready(self):
        print(f'Logged in as: {self.bot.user.name}')
        self.bot_log = self.bot.get_channel(508515073547960341)
        await self.bot_log.send(f'Starting up.. Running on {len(self.bot.guilds)} servers. Starttime: {self.bot.starttime}.')
        
    @commands.command()
    async def prefix(self, ctx, prefix: str):
        ''': Change the prefix'''
        if self.bot.db.prefix_set(ctx.guild.id, prefix):
            await ctx.channel.send(f'Prefix succesfully changed to `{prefix}`.')
        else:
            await ctx.channel.send(f'Failed setting prefix, please try again later.')

    @commands.command()
    async def latency(self, ctx):
        ''': See the latency between me and discord servers'''
        await ctx.channel.send(f'Current Latency: {self.bot.latency:.2f}ms')

    @commands.command()
    async def ping(self, ctx):
        ''': Check the current ping'''
        before = datetime.now()
        message = await ctx.channel.send('pong')
        diff = (datetime.now() - before)
        elapsed_ms = (diff.days * 86400000) + (diff.seconds * 1000) + (diff.microseconds / 1000)
        await message.edit(content=f'Current Ping: {elapsed_ms:.2f}ms')

    @commands.command()
    async def uptime(self, ctx):
        ''': See how long I've been online'''
        _uptime = (datetime.now().replace(microsecond=0) - self.bot.starttime)
        await ctx.channel.send(f'I\'ve been online for `{_uptime}`.')

    @commands.command(hidden=True)
    async def starttime(self, ctx):
        ''': See when I went online'''
        await ctx.channel.send(f'Running since: `{self.bot.starttime}`.')

    @commands.command(hidden=True)
    async def servertime(self, ctx):
        ''': See what my current time is'''
        await ctx.channel.send(f'Current Servertime: `{datetime.now().replace(microsecond=0)}`.')
    
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

    @commands.command()
    async def userinfo(self, ctx, *args):
        ''': Show info to user requesting or mentioned'''
        user = ctx.author
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        elif args:
            user = ctx.guild.get_member(int(args[0]))

        _age = (datetime.now() - user.created_at)
        age = timedelta(days=_age.days, seconds=_age.seconds)
        
        embed = discord.Embed(title=str(user), description=f'User Information', color=user.color)
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=f'User ID <{user.id}>')
        embed.add_field(name='Nickname', value=f'{user.display_name}')
        embed.add_field(name='Account Age', value=f'{age}')
        embed.add_field(name='Created At', value=f'{user.created_at.replace(microsecond=0)}')
        embed.add_field(name='Joined At', value=f'{user.joined_at.replace(microsecond=0)}')
        embed.add_field(name='Color', value=f'{user.color}')
        #embed.add_field(name='Region', value=f'{region}')
        await ctx.channel.send(embed=embed)
    
    @commands.command()
    async def botinfo(self, ctx):
        ''': Show info about the bot'''
        user = self.bot.user
        # _age = (datetime.now() - user.created_at)
        # age = timedelta(days=_age.days, seconds=_age.seconds)
        _uptime = (datetime.now().replace(microsecond=0) - self.bot.starttime)

        embed = discord.Embed(title='Maki', description=f'[*your digital assistant*](https://discordbots.org/bot/431485759304892416)', color=discord.Color(0x963826))
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_footer(text=user)
        embed.add_field(name='Uptime', value=_uptime)
        embed.add_field(name='Total Servers', value=len(self.bot.guilds))
        embed.add_field(name='Total Users', value=len(set(self.bot.get_all_members())))
        embed.add_field(name='Total Channels', value=len(set(self.bot.get_all_channels())))
        await ctx.channel.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Utils(bot))
