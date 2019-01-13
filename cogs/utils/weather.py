import discord
from discord.ext import commands
import pyowm
from datetime import datetime
from utils import Config

class Weather():
    def __init__(self, bot):
        self.bot = bot
        config = Config.get_config()
        try:
            self.owm = pyowm.OWM(config.get('owmKey', None))
        except Exception as ex:
            print(f"Exception - unloading extension Weather: {ex}")
            self.bot.unload_extension("cogs.utils.weather")

    @commands.command()
    async def weather(self, ctx, *location: str):
        location = ' '.join(str(loc) for loc in location)
        try:
            await ctx.channel.send(embed=self.weather_build_embed(location))
        except discord.errors.HTTPException as ex:  # can't send embed=None
            await ctx.channel.send(f'⚠️ Requested location `{location}` not found. Please try a different location.')
    
    def weather_build_embed(self, location):
        try:
            observation = self.owm.weather_at_place(location)    
        except pyowm.exceptions.api_response_error.NotFoundError as ex:
            return None
        w = observation.get_weather()
        temp_c = w.get_temperature('celsius')
        temp_f = w.get_temperature('fahrenheit')
        wind_mps = w.get_wind()
        wind_miph = w.get_wind('miles_hour')
        humidity = w.get_humidity()
        details = w.get_detailed_status()
        icon_url = w.get_weather_icon_url()

        temp_str = f"{temp_c.get('temp', None)}°C / {temp_f.get('temp', None)}°F"
        temp_max_str = f"{temp_c.get('temp_max', None)}°C / {temp_f.get('temp_max', None)}°F"
        temp_min_str = f"{temp_c.get('temp_min', None)}°C / {temp_f.get('temp_min', None)}°F"
        wind_str = f"{wind_mps.get('speed', 0)*3.6:.1f}km/h - {wind_miph.get('speed', 0):.1f}mph"

        embed = discord.Embed(title=f'{location.capitalize()}', description='*Weather today*', timestamp=datetime.utcnow(), color=discord.Color(0xcd8500))
        embed.set_thumbnail(url=icon_url)
        embed.set_footer(text='powered by openweathermap.org')
        embed.add_field(name='Avg. Temp', value=temp_str)
        embed.add_field(name='Weather', value=details.capitalize())
        embed.add_field(name='Max. Temp', value=temp_max_str)
        embed.add_field(name='Wind Speed', value=wind_str)
        embed.add_field(name='Min. Temp', value=temp_min_str)
        embed.add_field(name='Humidity', value=f'{humidity}%')

        return embed

def setup(bot):
    bot.add_cog(Weather(bot))