# -*- coding: utf-8 -*-

import discord
from discord import option, default_permissions

from utils import iso_to_datetime, date_string_to_timedelta


def selfpit(bot: discord.Client):
    @bot.slash_command(
        name="selfpit",
        description="Send yourself to the pit.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(send_messages=True)
    @option("time", str, description="<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.", required=True)
    async def handle_selfpit_slash(
        ctx: discord.ApplicationContext,
        time: str
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        delta = date_string_to_timedelta(time)
        if not delta:
            # Let the user know they fucked up.
            embed = {
                "type": "rich",
                "title": "Timeout error",
                "description": f"The time is not following the right format: {time}.",
                "color": 0x0aeb06,
                "fields": [
                    {
                        'name': 'time',
                        'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
                    }
                ],
                "footer": {
                    "text": f'{ctx.guild.name} Mod Team'
                }
            }
            await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)
            return

        if delta.total_seconds() < 3600 or delta.total_seconds() > 259200:
            # Let the user know there is a limit
            embed = {
                "type": "rich",
                "title": "Timeout error",
                "description": "Time can only be between 1h and 3d.",
                "color": 0x0aeb06,
                "fields": [],
                "footer": {
                    "text": f'{ctx.guild.name} Mod Team'
                }
            }
            await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)
            return

        timeout_info = bot.pitbot_module.get_user_timeout(ctx.user)
        extended = False
        guild_config = bot.guild_config[bot.guilds[0].id]
        log_channel = int(guild_config['log_channel'])
        ban_roles = [discord.Object(int(role)) for role in guild_config['ban_roles']]

        if not timeout_info:
            bot.pitbot_module.add_timeout(user=ctx.user, guild_id=ctx.guild.id,
                time=int(delta.total_seconds()), issuer_id=bot.user.id, reason="User requested to be pitted.")
        else:
            new_time = int(delta.total_seconds() + timeout_info['time'])
            timeout_info = bot.pitbot_module.extend_timeout(user=ctx.user, time=new_time)
            extended = True

        await ctx.user.add_roles(*ban_roles, reason="Requested to be timed out.")

        # Send information message to the mods
        await bot.send_embed_message(log_channel, "User Timeout", f"<@{ctx.user.id}> requested to be timed out for {time}.")

        # Now send a DM to a user and answer the request
        embed = {
            "type": "rich",
            "title": "/selfpit",
            "description": f"<@{ctx.user.id}> requested to be timed out for {time}.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Send a DM to the user
        info_message = f"You've requested to be pitted for {time}."
        if extended:
            info_message = f"Your timeout has been extended for {time} by request."

        await bot.send_embed_dm(ctx.user, "User Timeout", info_message)


def timeout(bot: discord.Client) -> None:
    @bot.slash_command(
        name="timeout",
        description="Send a user to the pit.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    @option("user", discord.User, description="User to be pitted.", required=True)
    @option("time", str, description="<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.", required=True)
    @option("reason", str, description="Optional: Reason for the pit.", required=False)
    async def handle_timeout_slash(
        ctx: discord.ApplicationContext,
        user: discord.User,
        time: str,
        reason: str
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        if not reason or reason is None:
            reason ="No reason specified."

        delta = date_string_to_timedelta(time)
        if not delta:
            embed = {
                "type": "rich",
                "title": "Timeout error",
                "description": f"The time is not following the right format: {time}.",
                "color": 0x0aeb06,
                "fields": [
                    {
                        'name': 'time',
                        'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
                    }
                ],
                "footer": {
                    "text": f'{ctx.guild.name} Mod Team'
                }
            }
            await ctx.send_followup(embed=discord.Embed.from_dict(embed))
            return
        
        timeout_info = bot.pitbot_module.get_user_timeout(ctx.user)
        extended = False
        guild_config = bot.guild_config[ctx.guild.id]
        log_channel = int(guild_config['log_channel'])
        ban_roles = [discord.Object(int(role)) for role in guild_config['ban_roles']]

        bot.pitbot_module.add_strike(user=user, guild_id=ctx.guild.id,
                    issuer_id=ctx.author.id, reason=reason)
        if not timeout_info:
            bot.pitbot_module.add_timeout(user=ctx.user, guild_id=ctx.guild.id,
                time=int(delta.total_seconds()), issuer_id=ctx.author.id, reason="Timeout issued by a mod.")
        else:
            new_time = int(delta.total_seconds() + timeout_info['time'])
            timeout_info = bot.pitbot_module.extend_timeout(user=ctx.user, time=new_time)
            extended = True

        await ctx.user.add_roles(*ban_roles, reason="Timeout issued by a mod.")

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/timeout",
            "description": f"<@{user.id}> was timed out for {time}.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Post information in 
        user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        if not bot.silent and log_channel:
            user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')

            strike_text = ""
            if len(user_strikes) > 0:
                strike_messages = []

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was timed out by <@{ctx.author.id}> for {time}."
            if extended:
                info_message = f"<@{user.id}>'s timeout was extended by <@{ctx.author.id}> for {time}."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]
            await bot.send_embed_message(log_channel, "User Timeout", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been pitted by {ctx.guild.name} mod staff for {time} for the following reason:\n\n{reason}"
        if extended:
                info_message = f"Your timeout has been extended by {ctx.guild.name} mod staff for {time} for the following reason:\n\n{reason}"

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {ctx.guild.name} (including this one).\r\n"+
                "If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {ctx.guild.name}.", 'inline': False}
        ]
        await bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)


def timeoutns(bot: discord.Client) -> None:
    @bot.slash_command(
        name="timeoutns",
        description="Send a user to the pit without a strike.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    @option("user", discord.User, description="User to be pitted.", required=True)
    @option("time", str, description="<1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.", required=True)
    @option("reason", str, description="Optional: Reason for the pit.", required=False)
    async def handle_timeoutns_slash(
        ctx: discord.ApplicationContext,
        user: discord.User,
        time: str,
        reason: str
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        if not reason or reason is None:
            reason ="No reason specified."

        delta = date_string_to_timedelta(time)
        if not delta:
            embed = {
                "type": "rich",
                "title": "Timeout error",
                "description": f"The time is not following the right format: {time}.",
                "color": 0x0aeb06,
                "fields": [
                    {
                        'name': 'time',
                        'value': 'The time parameter expects the following format: <1-2 digit number><one of: m, h, d> where m is minute, h is hour, d is day.'
                    }
                ],
                "footer": {
                    "text": f'{ctx.guild.name} Mod Team'
                }
            }
            await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)
            return
        
        timeout_info = bot.pitbot_module.get_user_timeout(ctx.user)
        extended = False
        guild_config = bot.guild_config[bot.guilds[0].id]
        log_channel = int(guild_config['log_channel'])
        ban_roles = [discord.Object(int(role)) for role in guild_config['ban_roles']]

        if not timeout_info:
            bot.pitbot_module.add_timeout(user=ctx.user, guild_id=ctx.guild.id,
                time=int(delta.total_seconds()), issuer_id=ctx.author.id, reason="Timeout issued by a mod.")
        else:
            new_time = int(delta.total_seconds() + timeout_info['time'])
            timeout_info = bot.pitbot_module.extend_timeout(user=ctx.user, time=new_time)
            extended = True

        await ctx.user.add_roles(*ban_roles, reason="Timeout issued by a mod.")

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/timeout",
            "description": f"<@{user.id}> was timed out for {time}.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Post information in 
        user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        if not bot.silent and log_channel:
            user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')

            strike_text = ""
            if len(user_strikes) > 0:
                strike_messages = []

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was timed out by <@{ctx.author.id}> for {time}."
            if extended:
                info_message = f"<@{user.id}>'s timeout was extended by <@{ctx.author.id}> for {time}."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]
            await bot.send_embed_message(log_channel, "User Timeout", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been pitted by {ctx.guild.name} mod staff for {time} for the following reason:\n\n{reason}"
        if extended:
                info_message = f"Your timeout has been extended by {ctx.guild.name} mod staff for {time} for the following reason:\n\n{reason}"

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {ctx.guild.name} (including this one).\r\n"+
                "If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {ctx.guild.name}.", 'inline': False}
        ]
        await bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)
