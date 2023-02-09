# -*- coding: utf-8 -*-

## Timeout ##
# A command to timeout people. #

import datetime

import discord

from modules.context import CommandContext, DMContext
from modules.command import Command, verify_permission
from utils import iso_to_datetime, date_string_to_timedelta, seconds_to_string
from log_utils import do_log


class Timeout(Command):
    def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = None, skip_strike: bool =False) -> None:
        super().__init__(pitbot, permission, dm_keywords)
        self.skip_strike = skip_strike

    @verify_permission
    async def execute(self, context: CommandContext) -> None:
        if len(context.params) == 0:
            await self.send_help(context)
            return

        user = None

        # We either need a mention or an ID as first parameter.
        if not context.mentions:
            user_id = context.params[0]
            # review its a "valid" snowflake
            if not len(user_id) > 16:
                await self.send_help(context)
                return

            user = self._module.get_user(user_id=user_id)

            if not user:
                user = int(context.params[0])

        else:
            user = context.mentions[0]

        try:
            if isinstance(user, int):
                user = await self._bot.get_guild(context.guild.id).fetch_member(user)
            elif isinstance(user, dict):
                user = await self._bot.get_guild(context.guild.id).fetch_member(int(user['discord_id']))
            await user.remove_roles(*context.ban_roles, reason="User released by a mod.")
        except discord.NotFound as ex:
            print(ex)
            fields = [
                {'name': 'Error', 'value': f"User {user} is not in the server and cannot be released.", 'inline': True},
            ]
            await self._bot.send_embed_message(context.log_channel, "Release user", color=0xb30000, fields=fields)
            return

        if len(context.params) == 1:
            await self._send_timeout_info(user, context)
            return

        amount = context.params[1]
        if not amount:
            await self.send_help(context)
            return
        delta = date_string_to_timedelta(amount)

        reason = ''
        if len(context.params) >= 2:
            reason = ' '.join(context.params[2:])

        if not self.skip_strike:
            self._bot.strikes_module.add_strike(user=user, guild_id=context.guild.id,
                issuer_id=context.author.id, reason=reason)

        timeout_info = self._module.get_user_timeout(user)
        extended = False

        if not timeout_info:
            timeout_info = self._module.add_timeout(user=user, guild_id=context.guild.id,
                time=int(delta.total_seconds()), issuer_id=context.author.id, reason=reason)
        else:
            new_time = int(delta.total_seconds() + timeout_info['time'])
            timeout_info = self._module.extend_timeout(user=user, time=new_time)
            extended = True

        await user.add_roles(*context.ban_roles, reason="Timeout issued by a mod.")
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'timeout'}, context=context)

        user_strikes = self._bot.strikes_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        if not context.is_silent and context.log_channel:
            user_timeouts = self._module.get_user_timeouts(user=user, status='expired')

            strike_text = "```No Previous Strikes```"
            if len(user_strikes) > 0:
                strike_messages = list()

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was timed out by <@{context.author.id}> for {amount}."
            if extended:
                info_message = f"<@{user.id}>'s timeout has been extended by <@{context.author.id}> for {amount}."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]

            await self._bot.send_embed_message(context.log_channel, "User Timeout", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been pitted by {context.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"
        if extended:
            info_message = f"Your active timeout in {context.guild.name} has been extended by {amount} for the following reason:\n\n{reason}"

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
                f"If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)

    async def dm(self, context: DMContext) -> None:

        timeout = self._module.get_user_timeout(context.author)

        if not timeout or timeout is None:
            await self._bot.send_embed_dm(context.author, "Timeout Info", "You don't have an active timeout right now.")
            return

        guild = await self._bot.get_guild(id=timeout['guild_id'])
        if not guild:
            guild = self._bot.default_guild

        issued_date = iso_to_datetime(timeout['created_date'])
        expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])
        delta = expire_date - datetime.datetime.now()
        expires_in = seconds_to_string(int(delta.total_seconds()))

        reason = timeout['reason'] if timeout['reason'] else ''

        description = f"You are currently timed out from {guild.name} and it will expire in {expires_in}."

        fields = [
            {'name': 'Reason', 'value': reason, 'inline': False},
            {'name': 'Info', 'value': "Type `strikes` to get more information about your strikes.", 'inline': False}
        ]

        await self._bot.send_embed_dm(context.author, "Timeout Info", description, fields=fields)
        await do_log(place="dm", data_dict={'event': 'command', 'command': 'timeout', 'author_id': context.author.id,
                                'author_handle': f'{context.author["username"]}#{context.author["discriminator"]}'})

    @verify_permission
    async def ping(self, context):
        if len(context.mentions) < 2 or len(context.params) < 3:
            return

        # by now we've already stablished mentions 0 is the bot
        user = context.mentions[1]
        amount = context.params[2]
        delta = date_string_to_timedelta(amount)
        if not delta:
            return

        reason = ''
        if len(context.params) > 4:
            reason = ' '.join(context.params[4:])
            
        await user.add_roles(context.ban_roles, reason="Timeout issued by a mod.")

        self._module.add_timeout(user=user, guild_id=context.guild.id,
                time=int(delta.total_seconds()), issuer_id=context.author.id, reason=reason)
        self._bot.strikes_module.add_strike(user=user, guild_id=context.guild.id,
                issuer_id=context.author.id, reason=reason)

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'timeout'}, context=context)

        user_strikes = self._bot.strikes_module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)
        if not context.is_silent and context.log_channel:
            # Send a smug notification on the channel
            description = f"<@{user.id}> has been sent to the pit for {amount}"
            image = {
                "url": self._bot.get_timeout_image(),
                "height": 0,
                "width": 0
            }
            await self._bot.send_embed_message(context.channel, "User Timeout", description, image=image)

            user_timeouts = self._module.get_user_timeouts(user=user, status='expired')

            strike_text = "```No Previous Strikes```"
            if len(user_strikes) > 0:
                strike_messages = list()

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was timed out by <@{context.author.id}> for {amount}."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]

            await self._bot.send_embed_message(context.log_channel, "User Timeout", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been pitted by {context.guild.name} mod staff for {amount} for the following reason:\n\n{reason}"

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
                f"If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user, "User Timeout", info_message, fields=fields)

    async def send_help(self, context: CommandContext) -> None:
        """Sends Help information to the channel"""
        fields = [
            {'name': 'Help', 'value': f"Use {context.command_character}timeout @user <time> <reason:optional> \
                to timeout a user for a set amount of time and add a strike to their account.", 'inline': False},
            {'name': 'Help2', 'value': f"Use {context.command_character}timeoutns @user <time> <reason:optional> \
                to timeout a user for a set amount of time without adding a strike to their account.", 'inline': False},
            {'name': '<time>', 'value': "Time allows the following format: <1-2 digit number><one of: s, m, h, d> where \
                s is second, m is minute, h is hour, d is day.", 'inline': False},
            {'name': 'Example', 'value': f"{context.command_character}timeout <@{self._bot.user.id}> 24h Being a bad bot", 'inline': False},
            {'name': 'Note:', 'value': f"Instead of @ing a user you can just provide their ID instead.", 'inline': False},
            {'name': 'Note2:', 'value': f"if the user has an active timeout already it will extend the duration instead.", 'inline': False}
        ]

        await self._bot.send_embed_message(context.channel, "User Timeout", fields=fields)

    async def _send_timeout_info(self, user: discord.User, context: CommandContext) -> None:
        timeout = self._module.get_user_timeout(user)

        if not timeout or timeout is None:
            await self._bot.send_embed_message(context.channel, "Timeout Info", "You don't have an active timeout right now.")
            return

        guild = await self._bot.get_guild(guild_id=timeout['guild_id'])
        if not guild:
            guild = self._bot.default_guild

        issued_date = iso_to_datetime(timeout['created_date'])
        expire_date = issued_date + datetime.timedelta(seconds=timeout['time'])
        delta = expire_date - datetime.datetime.now()
        expires_in = seconds_to_string(int(delta.total_seconds()))

        reason = timeout['reason'] if timeout['reason'] else ''

        description = f"<@{user.id}> is currently timed out by <@{timeout['issuer_id']}> and it will expire in {expires_in}."

        fields = [
            {'name': 'Reason', 'value': reason, 'inline': False}
        ]

        await self._bot.send_embed_message(context.channel, "Timeout Info", description, fields=fields)
