import discord
from discord.ext import commands
from omdb import OMDBClient
from utils import Config

class Movie():
    def __init__(self, bot):
        self.bot = bot
        config = Config.get_config()
        try:
            self.omdb = OMDBClient(apikey=config.get('omdbKey', None))
        except Exception as ex:
            self.bot.unload_extension("cogs.utils.movie")
        
    @commands.command()
    async def movie(self, ctx, *name: str):
        search = self.omdb.search_movie(name)
        selected_movie = None
        if len(search) > 1:
            if len(search) > 10:  # api should only give 10 movies, but let's just limit it
                search = search[:10]
            
            res = ''
            for index, movie in enumerate(search):
                res += f"{str(index)+'⃣'} {movie.get('title', None)} ({movie.get('year', None)})\n"
            res += ''
            embed = discord.Embed(title='Please choose a movie', description=res)
            mes = await ctx.channel.send(embed=embed)
            for index in range(0, len(search)):
                await mes.add_reaction(f"{str(index)+'⃣'}")
            def check(reaction, user):
                return reaction.message.id == mes.id and user == ctx.message.author
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            try: 
                await mes.clear_reactions()
            except Exception:
                error = 'Need manage_messages permission for full functionality.'
            await mes.edit(content=f'here is your movie', embed=None)
            

def setup(bot):
    bot.add_cog(Movie(bot))