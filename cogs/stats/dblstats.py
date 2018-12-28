import aiohttp
import sys, traceback
from utils import Config

class DBLStats():
    def __init__(self, bot):
        self.bot = bot

    async def post_count(self):
        if not self.token:  # can never happen theoretically 
            return

        payload = {"server_count": len(self.bot.guilds)}
        async with aiohttp.ClientSession() as aioclient:
            print(self.url, payload, self.headers)
            await aioclient.post(self.url, data=payload, headers=self.headers)
    
    async def on_ready(self):
        config = Config.get_config()
        try:
            self.token = config["dblapi"]
            self.headers = {"Authorization": self.token}
            self.url = f'https://discordbots.org/api/bots/{str(self.bot.user.id)}/stats'
        except:
            print("exception - unloading extension dblstats.")
            traceback.print_exc(file=sys.stdout)
            self.bot.unload_extension("cogs.utils.dblstats")
        await self.post_count()

    async def on_guild_join(self, guild):
        await self.post_count(self)

    async def on_guild_remove(self, guild):
        await self.post_count(self)

def setup(bot):
    bot.add_cog(DBLStats(bot))