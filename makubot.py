import asyncio
import discord
from discord.ext import commands
from discord import Game
import sys, traceback

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

initial_extensions = ['cogs.utils.owner',
                      'cogs.utils.utils',
                      'cogs.utils.remindme',
                      'cogs.utils.family',
                      'cogs.stats.emotes']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as ex:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bot.loop.create_task(list_servers())
bot.run(config['token'], bot=True, reconnect=True)
    
    