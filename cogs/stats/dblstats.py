import aiohttp
import sys, traceback
from utils import Config
from discord.ext import commands
import dbl


class DBLStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = Config.get_config()
        try:
            self.token = config["dblapi"]
        except Exception as ex:
            print(f"exception - unloading extension dblstats: {ex}")
            traceback.print_exc(file=sys.stdout)
            self.bot.unload_extension("cogs.utils.dblstats")
        self.dblpy = dbl.DBLClient(self.bot, self.token, autopost=True)

    # async def post_count(self):
    #     if not self.token:  # can never happen theoretically
    #         return

    #     payload = {"server_count": len(self.bot.guilds)}
    #     async with aiohttp.ClientSession() as aioclient:
    #         await aioclient.post(self.url, data=payload, headers=self.headers)

    async def on_ready(self):
        print('DBLStats ready.')
        #     self.headers = {"Authorization": self.token}
        #     self.url = f"https://discordbots.org/api/bots/{str(self.bot.user.id)}/stats"
        # except Exception as ex:
            
        # await self.post_count()

    # async def on_guild_join(self, guild):
    #     await self.post_count()

    # async def on_guild_remove(self, guild):
    #     await self.post_count()


def setup(bot):
    bot.add_cog(DBLStats(bot))
