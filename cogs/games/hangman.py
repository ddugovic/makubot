import random
import datetime
import discord
from discord.ext import commands


def get_random_word():
    with open("cogs/games/hangman_words.txt") as input_file:
        words = input_file.read().split("\n")
    return random.choice(words).lower()


class HangmanGame:
    def __init__(self):
        self.secret = ""
        self.guessed = list()
        self.unveiled = ""

    def new_game(self, difficulty=0):
        self.secret = get_random_word()
        self.set_unveiled()
        return self.unveiled

    def set_unveiled(self):
        new_unveil = ""
        for char in self.secret:
            if char in self.guessed:
                new_unveil += char
            else:
                new_unveil += "_"
        self.unveiled = new_unveil

    def new_input(self, guess):
        """
            new guess, return correct_guess, game_won
        """
        guess = guess.lower()
        if guess in self.guessed:  # already guessed, nothing happens
            return True, False
        if len(guess) > 1:
            if guess == self.secret:
                return True, True
            else:
                return False, False
        self.guessed.append(guess)
        self.set_unveiled()
        if guess in self.secret:
            if self.unveiled == self.secret:
                return True, True
            else:
                return True, False
        return False, False

    def get_game(self):
        return self.guessed, self.unveiled


class HangmanGameAll(HangmanGame):
    def __init__(self, owner_id):
        self.owner_id = owner_id
        self.player_cds = dict()
        super().__init__()

    def new_input(self, guess, player_id):
        if player_id in self.player_cds:
            if datetime.datetime.now() > self.player_cds[player_id]:
                self.player_cds.pop(player_id)
            else:
                return False, False
        # if not player_id in self.player_cds:
        correct, won = super().new_input(guess)
        if not correct:
            self.player_cds[player_id] = datetime.datetime.now() + datetime.timedelta(
                seconds=2.5
            )
        return correct, won

    def get_game(self):
        guessed, unveiled = super().get_game()
        return guessed, unveiled, self.player_cds.keys()


def create_emote_unveil(unveiled):
    emote_unveil = ""
    for char in unveiled:
        if char != "_":
            emote_unveil += f":regional_indicator_{char}:"
        else:
            emote_unveil += ":large_blue_circle:"
    return emote_unveil


def hangman_embed(unveiled, guessed, player_cds):
    description = "Everyone can guess. Invalid guess - 5s cooldown for player. \nGuess with single letters or the full word."
    embed = discord.Embed(
        title="Hangman - Free For All",
        description=description,
        color=discord.Color(0xCCCC00),
    )
    if guessed:
        embed.add_field(name="Guesses", value=", ".join(guessed), inline=False)
    embed.add_field(name="Word", value=create_emote_unveil(unveiled), inline=False)

    return embed


def hangman_embed_winner(secret, guessed, player, time):
    description = f"**Winner** - {player} || **Playtime**: {time}"
    embed = discord.Embed(
        title="Hangman - Free For All",
        description=description,
        color=discord.Color(0x008000),
    )
    embed.add_field(name="Secret Word", value=secret)
    return embed


def hangman_embed_timeout(secret):
    description = f"Game timed out after 5 minutes of inactivity."
    embed = discord.Embed(
        title="Hangman - Free For All",
        description=description,
        color=discord.Color(0x8B0000),
    )
    # embed.add_field(name=secret, value='test')
    return embed


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hangall(self, ctx):
        start_time = datetime.datetime.now()
        game = HangmanGameAll(ctx.author.id)
        unveiled = game.new_game()
        game_done = False

        embed = hangman_embed(unveiled, None, None)
        game_embed = await ctx.channel.send(embed=embed)

        def check(m):
            return m.channel == ctx.channel

        while not game_done:
            try:
                msg = await self.bot.wait_for("message", check=check, timeout=300)
            except asyncio.TimeoutError:
                embed = hangman_embed_timeout()
                await game_embed.edit(embed=embed)
            _, won = game.new_input(msg.content, msg.author.id)
            guessed, unveiled, player_cds = game.get_game()
            embed = hangman_embed(unveiled, guessed, player_cds)
            await game_embed.edit(embed=embed)
            if won:
                game_done = True
                # await ctx.channel.send(f'<@{msg.author.id}> won. Corret word: {unveiled}')
                embed = hangman_embed_winner(
                    unveiled, guessed, msg.author, datetime.datetime.now() - start_time
                )
                await game_embed.edit(embed=embed)


def setup(bot):
    bot.add_cog(Hangman(bot))
