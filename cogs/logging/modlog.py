from datetime import datetime
import discord
from discord.ext import commands
from asyncio import TimeoutError

class ModLog:
    def __init__(self, bot):
        self.bot = bot
        self.default_logging = {
            'messageDeleted': True,
            'memberJoined': False,
            'memberLeft': False,
            'memberKicked': True,
            'memberBanned': True,
            'memberUnbanned': True
        }

    async def on_message_delete(self, message):
        channel, key = self.get_channel_key(message.guild.id, 'messageDeleted')
        if not channel or not key:  # basically means disabled 
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
        try:
            async for log in message.guild.audit_logs(limit=1):
                if log.action == discord.AuditLogAction.message_delete:
                    responsible = log.user
        except: 
            await channel.send('⚠️ I\'m missing `view_audit_log` permission. Some log information might be displayed incorrectly.')
        embed.set_footer(text=f'Responsible: {responsible}')
        await channel.send(embed=embed)

    async def on_member_join(self, member):
        channel, key = self.get_channel_key(member.guild.id, 'memberJoined')
        if not channel or not key:  # basically means disabled 
            return
        embed = discord.Embed(title=str(member), description='*Member joined*', color=discord.Color(0x40e0d0), timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar_url)
        await channel.send(embed=embed)
    
    async def on_member_remove(self, member):
        channel, key_left = self.get_channel_key(member.guild.id, 'memberLeft')
        if not channel:
            return
        _, key_kicked = self.get_channel_key(member.guild.id, 'memberKicked')
        banned, _, _ = await self.check_member_log(member.guild, member, discord.AuditLogAction.ban)  # check ban first
        if banned:
            return
        kicked, responsible, reason = await self.check_member_log(member.guild, member, discord.AuditLogAction.kick)
        if kicked: 
            if not key_kicked:
                return  # not enabled
            desc = '*Member kicked*'
            color = discord.Color(0x6d0000)
        else:
            if not key_left:
                return  # not enabled
            desc = '*Member left*'
            color = discord.Color(0x40e0d0)
        embed = discord.Embed(title=str(member), description=desc, color=color, timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar_url)
        if kicked:
            if reason:
                embed.add_field(name='Reason', value=reason)
            embed.set_footer(text=f'Responsible: {responsible}')
        await channel.send(embed=embed)

    async def on_guild_role_create(self, role):
        pass

    async def on_guild_role_delete(self, role):
        pass
    
    async def on_guild_role_update(self, before, after):
        pass
    
    async def on_member_ban(self, guild, member):
        channel, key = self.get_channel_key(guild.id, 'memberBanned')
        if not channel or not key:  # basically means disabled 
            return
        banned, responsible, reason = await self.check_member_log(guild, member, discord.AuditLogAction.ban)
        desc = '*Member banned*'
        color = discord.Color(0x6d0000)
        embed = discord.Embed(title=str(member), description=desc, color=color, timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar_url)
        if banned:
            if reason:
                embed.add_field(name='Reason', value=reason)
            embed.set_footer(text=f'Responsible: {responsible}')
        await channel.send(embed=embed)
    
    async def on_member_unban(self, guild, member):
        channel, key = self.get_channel_key(guild.id, 'memberUnbanned')
        if not channel or not key:  # basically means disabled 
            return
        unbanned, responsible, reason = await self.check_member_log(guild, member, discord.AuditLogAction.unban)
        desc = '*Member unbanned*'
        color = discord.Color(0x006d00)
        embed = discord.Embed(title=str(member), description=desc, color=color, timestamp=datetime.now())
        embed.set_thumbnail(url=member.avatar_url)
        if unbanned:
            if reason:
                embed.add_field(name='Reason', value=reason)
            embed.set_footer(text=f'Responsible: {responsible}')
        await channel.send(embed=embed)

    def get_channel(self, guild_id):
        ''' returns channel instance to be logged to '''
        logging = self.bot.db.logging_get(guild_id)
        channel_id = logging.get('channel', None)
        channel = self.bot.get_channel(channel_id)
        return channel
    
    def key_enabled(self, guild_id, key):
        logging = self.bot.db.logging_get(guild_id)
        if "channel" in logging:
            return logging.get(key, False)
        return False
    
    def get_channel_key(self, guild_id, key):
        return self.get_channel(guild_id), self.key_enabled(guild_id, key)

    async def check_member_log(self, guild, member, action, limit=1):
        try:
            async for log in guild.audit_logs(limit=limit):
                if log.action == action:
                    if log.target == member:
                        return True, log.user, log.reason
        except Exception as ex: 
            print(f'exception occured {ex}')
            pass  # cannot send error message from here.
            #await channel.send('⚠️ I\'m missing `view_audit_log` permission. Some log information might be displayed incorrectly.')
        return False, None, None

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
                if self.bot.db.logging_set_key(ctx.guild.id, key, _state):
                    await ctx.channel.send(f'Successfully {state}d `{key}`.')
                else:
                    await ctx.channel.send(f'Failed setting logging. Please configure channel first.')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def logsetup(self, ctx):
        if not await self.permissions_check(ctx):
            return
        abort_str = f'⚠️ Something went wrong while setting the channel. Aborting.'
        # Channel
        channel = self.get_channel(ctx.guild.id)
        channel_str = f'It is currently **not** set.\
                        \n - Please link the channel that you want to log to.'
        if channel:
            channel_str = f'It is currently set to: <#{channel.id}>\
                            \n - If you don\'t wish to change it answer with `no`.\
                            \n - If you want to disable logging write `disable`.'      
        await ctx.channel.send(f'Hey there! I\'ll guide you through the logging setup.\
                                \nWhat `channel` do you want to log to? {channel_str}')

        def check_channel(m):
            return (m.channel_mentions or
                    m.content.lower() == 'no' or 
                    m.content.lower() == 'disable') and m.channel == ctx.channel
        try:
            answer = await ctx.bot.wait_for('message', timeout=60, check=check_channel)
            mes = f'Logging channel not changed.'
            if answer.channel_mentions:
                channel = answer.channel_mentions[0]
                mes = abort_str
                if self.bot.db.logging_set_channel(ctx.guild.id, channel.id):
                    mes = f'✔️ Logging channel set to <#{channel.id}>.'

            elif channel and answer.content.lower() == 'disable':
                mes = abort_str
                if self.bot.db.logging_set_channel(ctx.guild.id, None):
                    mes = f'Logging disabled. Setup done.'
                    return  # ending setup
            elif not channel:
                mes = f'⚠️ Logging channel not set. Please restart the command and set a channel to continue.'
            await ctx.channel.send(mes)
        except TimeoutError:
            await ctx.channel.send(f'⚠️ No answer received within timeout. Stopping.')
            return
        
        logging = self.bot.db.logging_get(ctx.guild.id)
        logging.pop('channel', None)
        full_logging = {**self.default_logging, **logging}  # merge the dicts in case DB misses keys
        for key, val in full_logging.items():
            state = 'disabled'
            if val:
                state = 'enabled'
            await ctx.channel.send(f'Do you wish to enable `{key}`? Currently set to: `{state}`\n - `yes` to enable, `no` to disable.')
            try:
                def check(m):
                    return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == ctx.channel
                answer = await ctx.bot.wait_for('message', timeout=60, check=check)
                new_state = False
                if answer.content.lower() == 'yes':
                    new_state = True
                self.bot.db.logging_set_key(ctx.guild.id, key, new_state)
                print(f'new_state for {key} = {new_state}')
                await ctx.channel.send(f'✔️ Set `{key}` to `{new_state}`.')
            except TimeoutError:
                await ctx.channel.send(f'⚠️ No answer received within timeout. Stopping.')
                return

    async def permissions_check(self, ctx):
        ''' Sends message and returns False if permissions are missing '''
        permissions = {
            'view_audit_log': '❌',
        }
        if ctx.guild.me.guild_permissions.view_audit_log:
            permissions['view_audit_log'] = '✔️'
        permission_str = 'Checking permissions.. \n'
        permissions_granted = True
        for key, val in permissions.items():
            permission_str += f'{val} - `{key}`\n'
            if val == '❌':
                permissions_granted = False
        if not permissions_granted:
            await ctx.channel.send(f'{permission_str}⚠️ Please grant the needed permissions and run the command again.')
            return False
        return True



def setup(bot):
    bot.add_cog(ModLog(bot))