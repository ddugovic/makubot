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
# import config access
from utils import Config

config = Config.get_config()

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
    await bot.change_presence(activity=Game(config['game']))

async def list_servers():
    await bot.wait_until_ready()
    while not bot.is_closed:
        print("Current servers:")
        for server in bot.servers:
            print(server.name)
        await asyncio.sleep(600)


bot.add_cog(Utils(bot))
bot.add_cog(Owner(bot))
bot.loop.create_task(list_servers())
bot.run(config['token'])
    
    