# -*- coding: utf-8 -*-

import discord
from discord import option, default_permissions

from utils import iso_to_datetime


def release(bot: discord.Bot) -> None:
    @bot.slash_command(
        name="release",
        description="Send a user to the pit without a strike.",
        guild_ids=[bot.guilds[0].id]
    )
    @default_permissions(moderate_members=True)
    @option("user", discord.User, description="User to be released.", required=True)
    @option("amend", bool, description="Remove last strike.", required=False)
    async def handle_timeout_slash(
        ctx: discord.ApplicationContext,
        user: discord.User,
        amend: bool
    ) -> None:

        # Defer the message so we dont fuck up the command
        await ctx.response.defer(ephemeral=True)
        issued_by = ctx.user
        guild_config = bot.guild_config[ctx.guild.id]
        ban_roles = [discord.Object(int(role)) for role in guild_config['ban_roles']]

        await user.remove_roles(*ban_roles, reason="User released by a mod.")

        timeout_info = bot.pitbot_module.expire_timeout(user=user)
        strike_info = None

        if amend:
            strike_info = bot.pitbot_module.delete_strike(user=user)

        # Answer the request
        embed = {
            "type": "rich",
            "title": "/release",
            "description": f"<@{user.id}> was released from the pit.",
            "color": 0x6658ff,
            "fields": [],
            "footer": {"text": f'{ctx.guild.name} Mod Team'}
        }
        await ctx.send_followup(embed=discord.Embed.from_dict(embed), ephemeral=True)

        # Post information in log_channel
        log_channel = int(guild_config['log_channel'])
        user_strikes = bot.pitbot_module.get_user_strikes(user, sort=('_id', -1), partial=False)
        user_timeouts = bot.pitbot_module.get_user_timeouts(user=user, status='expired')
        
        if not bot.is_silent and log_channel:
            strike_text = ""
            if len(user_strikes) > 0:
                strike_messages = list()

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> wasn't timed out."
            if timeout_info:
                info_message = f"<@{user.id}> was released by <@{issued_by.id}>."

            if strike_info:
                info_message += "\r\n\r\nUser's last strike was deleted."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]

            await bot.send_embed_message(log_channel, "Release user", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been released from the pit by {ctx.guild.name} mod staff."
        if strike_info:
                info_message += "\r\n\r\nYour last strike was additionally deleted."

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {ctx.guild.name} (including this one).", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {ctx.guild.name}.", 'inline': False}
        ]

        await bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)
