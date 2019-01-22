import json
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
        ''': IMDb movie search

        movie title
        '''
        try:
            search = self.omdb.search_movie(name)
        except Exception as ex:
            await ctx.channel.send(f'Daily limit reached. Unfortunately the free omdb API only supports 1000 requests per day.')
            return
        selected_movie = None
        if len(search) > 1:
            if len(search) > 10:  # api should only give 10 movies, but let's just limit it
                search = search[:10]
            
            res = ''
            numbers = list()
            for index, movie in enumerate(search):
                numbers.append(str(index)+'⃣')
                res += f"{numbers[index]} {movie.get('title', None)} ({movie.get('year', None)})\n"
            res += ''
            embed = discord.Embed(title='Please choose a movie', description=res)
            mes = await ctx.channel.send(embed=embed)
            for index in range(0, len(search)):
                await mes.add_reaction(f"{str(index)+'⃣'}")
            def check(reaction, user):
                return reaction.message.id == mes.id and user == ctx.message.author
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            number = numbers.index(reaction.emoji)
            selected_movie = search[number]
        else:
            selected_movie = search[0]
        movie = self.omdb.request(i=selected_movie.get('imdb_id', None))
        movie = json.loads(movie.content)
        error=''
        plot = None
        if movie['Plot'] != 'N/A':
            plot = movie['Plot']
        awards = None
        if movie['Awards'] != 'N/A':
            awards = movie['Awards']
        poster = None
        if movie['Poster'] != 'N/A':
            poster = movie['Poster']
        
        embed = discord.Embed(title=movie.get('Title', None), description=plot, url=f'https://www.imdb.com/title/{movie.get("imdbID",None)}')
        embed.add_field(name='Year', value=movie.get('Year', None))
        if poster is not None:
            embed.set_thumbnail(url=poster)
        embed.add_field(name='Genre', value=movie.get('Genre', None))
        embed.add_field(name='Actors', value=movie.get('Actors', None))
        embed.add_field(name='Director', value=movie.get('Director', None))
        if awards is not None:
            embed.add_field(name='Awards', value=awards)
        embed.add_field(name='IMDb Rating', value=movie.get('imdbRating', None))
        for r in movie.get('Ratings', list()):
            embed.add_field(name=r.get('Source', None), value=r.get('Value', None))
        if 'mes' in locals():
            try: 
                await mes.clear_reactions()
            except Exception:
                error = '⚠️ *Need manage_messages permission for full functionality.*'
            await mes.edit(content=error, embed=embed)
        else:
            await ctx.channel.send(embed=embed)
            

def setup(bot):
    bot.add_cog(Movie(bot))