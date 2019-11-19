import discord
from discord.ext import commands
from utils import Config

import subprocess
import sys
import traceback


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(hidden=True)
    async def defaultprefix(self, ctx, prefix: str):
        """ changes the default prefix """
        try:
            Config.set_prefix(prefix)
            self.bot.default_prefix = prefix
        except ValueError:
            await ctx.channel.send(f"Prefix invalid or not all Values set properly.")

        await ctx.channel.send(f"Prefix changed to `{prefix}`")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def exec(self, ctx, *command: str):
        try:
            with subprocess.Popen(
                [*list(command)], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                out = proc.stdout.read().decode()[0:1994]  # max 2000 signs per message
                err = proc.stderr.read().decode()[0:1994]
                if out:
                    await ctx.channel.send("*stdout*:\n```" + out + "```")
                if err:
                    await ctx.channel.send("*stderr*:\n```" + err + "```")
        except:
            await ctx.channel.send(f"Command `{command}` failed.")
            traceback.print_exc()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def restart(self, ctx):
        await ctx.channel.send(f"Restarting..")
        sys.exit()

    @commands.is_owner()
    @commands.command(hidden=True)
    async def load(self, ctx, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def unload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")

    @commands.is_owner()
    @commands.command(hidden=True)
    async def reload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f"**`ERROR:`** {type(e).__name__} - {e}")
        else:
            await ctx.send("**`SUCCESS`**")


def setup(bot):
    bot.add_cog(Owner(bot))
