import discord
from discord.ext import commands
from utils import Config

import asyncio

import time
from datetime import timedelta

import re


UNITS = {"s":"seconds", "m":"minutes", "h":"hours", "d":"days", "w":"weeks"}

def convert_to_delta(s):
    _unit = {}
    for t in s.split(' '):
        count = int(t[:-1])
        unit = UNITS[ t[-1] ]
        _unit[unit] = count
    td = timedelta(**_unit)
    return td


class RemindMe():
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.check_reminders())

    async def check_reminders(self):
        """ check reminders every second """
        await self.bot.wait_until_ready()
        while True:
            expired = self.bot.db.reminders_get_expired()
            if expired:
                for reminder in expired:
                    mes = await self.send_reminder(reminder)
                    if mes:
                        self.bot.db.reminders_delete(reminder['_id'])
            await asyncio.sleep(1)
    
    async def send_reminder(self, reminder):
        note = reminder['note']
        user_id = reminder['userId']
        if reminder['sendDM']:
            user = self.bot.get_user(user_id)
            channel = user.dm_channel
            if not channel:
                channel = await user.create_dm()
            try:      
                return await channel.send(note)
            except discord.errors.Forbidden:
                channel_id = reminder['channelId']
                channel = self.bot.get_channel(channel_id)
                return await channel.send(f'Hey <@{user_id}>, I\'m unfortunately not allowed to send you a direct message. Here is your reminder: "{note}".')
        else:
            channel_id = reminder['channelId']
            channel = self.bot.get_channel(channel_id)
            return await channel.send(f'<@{user_id}> "{note}"')


    def extract_reminder(self, ctx, _time, args):
        user_id = ctx.message.author.id
        guild_id = ctx.message.guild.id
        channel_id = ctx.message.channel.id
        note = ' '.join(args)
        regex = r"([0-9]+[smhdw])"
        _time = ' '.join(re.findall(regex, str(_time)))
        td = convert_to_delta(_time)
        return td, note, user_id, channel_id, guild_id

    @commands.command()
    async def remindme(self, ctx, _time, *args: str):
        td, note, user_id, channel_id, guild_id = self.extract_reminder(ctx, _time, args)
        self.bot.db.reminders_add(td, note, user_id, channel_id, guild_id, False)
        await ctx.channel.send(f'Reminder set in {td} for "{note}".')
    
    @commands.command()
    async def dmme(self, ctx, _time, *args: str):
        if not await self.dmtest(ctx.author):
            await ctx.channel.send(f'I do not have permission to send you a direct message. Please enable "**Allow direct messages from server members**" in your Privacy Settings or use `remindme` instead.')
            return
        td, note, user_id, channel_id, guild_id = self.extract_reminder(ctx, _time, args)
        self.bot.db.reminders_add(td, note, user_id, channel_id, guild_id, True)
        await ctx.channel.send(f'Reminder set in {td} for "{note}".')

    async def dmtest(self, user):
        channel = await user.create_dm()
        try:
            await channel.send()
        except discord.errors.Forbidden:
            return False
        except:  # any other exception most likely means it works
            return True

def setup(bot):
    bot.add_cog(RemindMe(bot))