import asyncio
import os
from datetime import datetime
from time import time

import discord
from discord.ext import commands
from discord import Game
# import cogs
from cogs.utils import Owner
from cogs.utils import Utils
from cogs.utils import RemindMe
from cogs.stats import Emotes
# import config access
from utils import Config
from utils import Database



def get_prefix(bot, message):
    # TODO: change to server prefix
    prefix = Config.get_config()['prefix']
    # prefix = bot.config.data.get('servers').get(str(message.guild.id)).get('prefix')
    if not prefix:
        prefix = '.'
    return commands.when_mentioned_or(*prefix)(bot, message)

bot = commands.AutoShardedBot(command_prefix=get_prefix)

@bot.event
async def on_ready():
    config = Config.get_config()
    await bot.change_presence(activity=Game(config['game']))

async def list_servers():
    await bot.wait_until_ready()
    while True:
        print("Current servers:")
        for server in bot.guilds:
            print(server.name)
        await asyncio.sleep(600)


config = Config.get_config()
bot.db = Database(config.get('mongodb', None))

bot.add_cog(Utils(bot))
bot.add_cog(Owner(bot))
bot.add_cog(RemindMe(bot))
bot.add_cog(Emotes(bot))

bot.loop.create_task(list_servers())
bot.run(config['token'])
    
    