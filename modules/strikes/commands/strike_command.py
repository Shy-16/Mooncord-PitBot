# -*- coding: utf-8 -*-

## Strike ##
# Strike related commands. #

import discord

from modules.context import CommandContext, DMContext
from modules.command import Command, verify_permission
from utils import iso_to_datetime
from log_utils import do_log


class Strike(Command):
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
        except discord.NotFound as ex:
            print(ex)
            fields = [
                {'name': 'Error', 'value': f"User {user} is not in the server and cannot be released.", 'inline': True},
            ]
            await self._bot.send_embed_message(context.log_channel, "Release user", color=0xb30000, fields=fields)
            return

        if len(context.params) > 1:
            if context.params[1] == "add":
                await self._do_add_strike(user, context)
                return
            elif context.params[1] == "exp" or context.params[1] == "expire":
                await self._do_expire_strike(user, context)
                return
            elif context.params[1] == "del" or context.params[1] == "delete":
                await self._do_delete_strike(user, context)
                return
            elif context.params[1] == "verbose":
                await self._do_show_strikes(user, context, verbose=True)
                return
            else:
                await self.send_help(context)
                return

        await self._do_show_strikes(user, context)

    async def dm(self, context: DMContext) -> None:
        """Reply to user dm"""

        user_strikes = self._module.get_user_strikes(context.author, sort=('_id', -1))

        active_strike_text = '```No active strikes```'
        expired_strike_text = '```No previous strikes```'
        if len(user_strikes) > 0:
            active_strike_messages = []
            expired_strike_messages = []

            for strike in user_strikes[:5]:
                date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                message = f"{date} Striked for {strike['reason'][0:90]} - {strike['_id']}"
                active_strike_messages.append(message) if strike['status'] == 'active' else expired_strike_messages.append(message)

            active_strike_text = "```" + "\r\n".join(active_strike_messages) + "```" if len(active_strike_messages) > 0 else '```No active strikes```'
            expired_strike_text = "```" + "\r\n".join(expired_strike_messages) + "```" if len(expired_strike_messages) > 0 else '```No previous strikes```'

        info_message = f"You have {len(user_strikes)} total strikes."

        fields = [
            {'name': 'Active Strikes', 'value': active_strike_text, 'inline': False},
            {'name': 'Expired Strikes', 'value': expired_strike_text, 'inline': False}
        ]

        await self._bot.send_embed_dm(context.author, "Strikes Info", info_message, fields=fields)
        await do_log(place="dm", data_dict={'event': 'command', 'command': 'strikes', 'author_id': context.author.id,
                                'author_handle': f'{context.author.name}#{context.author.discriminator}'})

    async def _do_show_strikes(self, user: discord.User, context: CommandContext, verbose: bool = False) -> None:
        """Shows information about strikes of a user"""
        if not verbose:
            user_strikes = self._module.get_user_strikes(user, status='active')
            description = f"<@{user.id}> has {len(user_strikes)} active strikes."
            await self._bot.send_embed_message(context.log_channel, "User Strikes", description)
            await do_log(place="guild", data_dict={'event': 'command', 'command': 'show_strikes'}, context=context)
            return

        user_strikes = self._module.get_user_strikes(user, sort=('_id', -1), partial=False)

        active_strike_text = '```No active strikes```'
        expired_strike_text = '```No previous strikes```'
        if len(user_strikes) > 0:
            active_strike_messages = list()
            expired_strike_messages = list()

            for strike in user_strikes[:5]:
                date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                message = f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}"
                active_strike_messages.append(message) if strike['status'] == 'active' else expired_strike_messages.append(message)

            active_strike_text = "```" + "\r\n".join(active_strike_messages) + "```" if len(active_strike_messages) > 0 else '```No active strikes```'
            expired_strike_text = "```" + "\r\n".join(expired_strike_messages) + "```" if len(expired_strike_messages) > 0 else '```No previous strikes```'

        info_message = f"<@{user.id}> has {len(user_strikes)} total strikes."

        fields = [
            {'name': 'Active Strikes', 'value': active_strike_text, 'inline': False},
            {'name': 'Previous Strikes', 'value': expired_strike_text, 'inline': False}
        ]

        await self._bot.send_embed_message(context.log_channel, "Strikes Info", info_message, fields=fields)
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'show_strikes'}, context=context)

    async def _do_add_strike(self, user: discord.User, context: CommandContext) -> None:
        """Adds a strike to a user"""
        reason = 'No reason specified'
        if len(context.params) >= 2:
            reason = ' '.join(context.params[2:])

        self._module.add_strike(user=user, guild_id=context.guild.id,
            issuer_id=context.author.id, reason=reason)

        user_strikes = self._module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        strike_text = "```No Previous Strikes```"
        if len(user_strikes) > 0:
            strike_messages = list()

            for strike in user_strikes[:5]:
                date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

            strike_text = "```" + "\r\n".join(strike_messages) + "```"

        info_message = f"A strike was added to <@{user.id}>."

        fields = [
            {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': False},
            {'name': '\u200B', 'value': strike_text, 'inline': False}
        ]

        await self._bot.send_embed_message(context.log_channel, "User Strike", info_message, fields=fields)

        # DM the user with the information
        info_message = f"{context.guild.name} mod staff has added a strike to your account with the following reason:\n\n{reason}"
        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (including this one).\r\n"+
                "If you receive a few more pits, your following punishments will be escalated, most likely to a temporary or permanent ban.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]
        await self._bot.send_embed_dm(user, "User Strikes", info_message, fields=fields)
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'add_strikes'}, context=context)

    async def _do_expire_strike(self, user: discord.User, context: CommandContext) -> None:
        """Sets a strike to expire"""
        if len(context.params) < 2:
            await self.send_help(context)
            return

        strike_id = context.params[2]
        strike_info = self._module.expire_strike(user=user, strike_id=strike_id)
        if strike_info is None:
            await self._bot.send_embed_message(context.channel, "User Strikes", "The strike wasn't found or couldn't be removed.")
            return

        user_strikes = self._module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)
        strike_text = "```No Previous Strikes```"
        if len(user_strikes) > 0:
            strike_messages = list()

            for strike in user_strikes[:5]:
                date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

            strike_text = "```" + "\r\n".join(strike_messages) + "```"

        info_message = f"A strike was updated to expired status for <@{user.id}>."

        fields = [
            {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': False},
            {'name': '\u200B', 'value': strike_text, 'inline': False}
        ]

        await self._bot.send_embed_message(context.log_channel, "User Strikes", info_message, fields=fields)

        # DM the user with the information
        info_message = f"{context.guild.name} mod staff has set one of your strikes as expired."

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (excluding this one).", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user, "User Strikes", info_message, fields=fields)

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'remove_strikes'}, context=context)

    async def _do_delete_strike(self, user: discord.User, context: CommandContext) -> None:
        """Deletes a strike"""
        if len(context.params) < 2:
            await self.send_help(context)
            return

        strike_id = context.params[2]
        strike_info = self._module.delete_strike(user=user, strike_id=strike_id)
        if strike_info is None:
            await self._bot.send_embed_message(context.channel, "User Strikes", "The strike wasn't found or couldn't be removed.")
            return

        user_strikes = self._module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)
        strike_text = "```No Previous Strikes```"
        if len(user_strikes) > 0:
            strike_messages = list()

            for strike in user_strikes[:5]:
                date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

            strike_text = "```" + "\r\n".join(strike_messages) + "```"

        info_message = f"A strike was deleted for <@{user.id}>."

        fields = [
            {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': False},
            {'name': '\u200B', 'value': strike_text, 'inline': False}
        ]

        await self._bot.send_embed_message(context.log_channel, "User Strikes", info_message, fields=fields)

        # DM the user with the information
        info_message = f"{context.guild.name} mod staff has deleted a strike from your account."

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name} (excluding this one).", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user, "User Strikes", info_message, fields=fields)
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'remove_strikes'}, context=context)
