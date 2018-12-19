import discord
from discord.ext import commands
import re


class Emotes:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author != self.bot.user:
            emotes = self.get_emotes(message.content)
            guild_id = message.guild.id
            self.bot.db.emotes_add(guild_id, emotes)


    def get_emotes(self, message):
        regex = re.compile(r':[A-Za-z0-9]+:')
        result = regex.findall(message)
        result = [r.replace(':', '') for r in result]
        return result

    @commands.command()
    async def count(self, ctx, emote: str):
        emote = self.get_emotes(emote)[0]
        guild_id = ctx.guild.id
        count = self.bot.db.emotes_count(guild_id, emote)
        message = f':{emote}: was used `{str(count)}` times.'
        await ctx.channel.send(message)

    @commands.command()
    async def top(self, ctx, *args):
        num = 5
        emote = None
        if len(args) == 2:
            try: 
                num = int(args[0])
                emote = args[1]
            except ValueError:
                try:
                    num = int(args[1])
                    emote = args[0]
                except ValueError:
                    pass
        elif len(args) == 1:
            try:
                num = int(args[0])
            except ValueError:
                emote = args[0]
        guild_id = ctx.guild.id
        top_emotes = self.bot.db.emotes_get_top(guild_id, num, emote)
            
        