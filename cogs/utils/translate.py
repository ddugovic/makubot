import discord
from discord.ext import commands
from utils import Config

from google.cloud import translate

langs = {
    '🇩🇪': 'de',
    '🇦🇹': 'de',
    '🇬🇧': 'en',
    '🇺🇸': 'en',
    '🇫🇷': 'fr',
    '🇪🇸': 'es'
}

class Translate():
    def __init__(self, bot):
        self.bot = bot
        self.translator = translate.Client()
    
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji in langs:
            lang = langs[reaction.emoji]
            message = str(reaction.message.clean_content)
            translated = self.translator.translate(message, target_language=lang)
            translated_text = translated['translatedText']
            embed = discord.Embed(title='Translation')
            embed.add_field(name='Message', value=message)
            embed.add_field(name=reaction.emoji, value=translated_text)
            channel =  reaction.message.channel
            await channel.send(embed=embed)