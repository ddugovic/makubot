from datetime import datetime
import discord
from discord.ext import commands

class ModLog:
    def __init__(self, bot):
        self.bot = bot

    async def on_message_delete(self, message):
        channel_id = self.logging_enabled(message.guild.id, 'messageDeleted')
        if channel_id is None:
            return
        embed = discord.Embed(description='*message deleted*', color=discord.Color(0x8B0000), timestamp=datetime.now())
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        async for mes in message.channel.history(limit=3, before=message, reverse=True):
            val = mes.clean_content
            if mes.embeds:
                val = '*unable to display embed in log*.'
            embed.add_field(name=mes.author, value=val, inline=False)
        embed.add_field(name=message.author, value='🚫️ ' + message.clean_content, inline=False)

        responsible = message.author
        channel = self.bot.get_channel(channel_id) 
        try:
            async for log in message.guild.audit_logs(limit=1):
                if log.action == discord.AuditLogAction.message_delete:
                    responsible = log.user
        except: 
            await channel.send('⚠️ I\'m missing `view_audit_log` permission. Some log information might be displayed incorrectly.')
        embed.set_footer(text=f'Responsible: {responsible}')
        await channel.send(embed=embed)

    def logging_enabled(self, guild_id, key):
        ''' returns log channel ID if enabled and None if not '''
        logging = self.bot.db.logging_get(guild_id)
        if "channel" in logging:
            if key in logging:
                if logging[key]:
                    return logging['channel']
        return None
    
    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def logchannel(self, ctx, channel_id:int):
        if not ctx.guild.me.guild_permissions.view_audit_log:
            await ctx.channel.send(f'I need `view_audit_log` permission for this feature. Please provide this permission and try again.')
            return
        if self.bot.db.logging_set_channel(ctx.guild.id, channel_id):
            await ctx.channel.send(f'Successfully set log channel to <#{channel_id}>.')
        else:
            await ctx.channel.send(f'Failed to set log channel. Please try again.')
        

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def logging(self, ctx, key: str, state: str):
        if key in ['messageDeleted']:
            if state.lower() in ['enable', 'disable']:
                if state.lower() == 'enable':
                    _state = True
                else:
                    _state = False  
                if self.bot.db.logging_enable_disable(ctx.guild.id, key, _state):
                    await ctx.channel.send(f'Successfully {state}d `{key}`.')
                else:
                    await ctx.channel.send(f'Failed setting logging. Please configure channel first.')


def setup(bot):
    bot.add_cog(ModLog(bot))