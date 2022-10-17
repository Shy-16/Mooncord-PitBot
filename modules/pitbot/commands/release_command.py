# -*- coding: utf-8 -*-

## Release ##
# A command to release people. #

from discord.errors import NotFound

from modules.context import CommandContext
from modules.command import Command, verify_permission
from utils import iso_to_datetime
from log_utils import do_log


class Release(Command):
    def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = None) -> None:
        super().__init__(pitbot, permission, dm_keywords)

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
        except NotFound as ex:
            print(ex)
            fields = [
                {'name': 'Error', 'value': f"User {user} is not in the server and cannot be released.", 'inline': True},
            ]
            await self._bot.send_embed_message(context.log_channel, "Release user", color=0xb30000, fields=fields)
            return
        
        amend = False
        if len(context.params) > 1:
            if context.params[1].lower() == "amend":
                amend = True

        self._module.expire_timeout(user=user)
        strike_info = None

        if amend:
            strike_info = self._module.delete_strike(user=user)

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'release'}, context=context)

        user_strikes = self._module.get_user_strikes(user, sort=('_id', -1), status='active', partial=False)

        if not context.is_silent and context.log_channel:
            user_timeouts = self._module.get_user_timeouts(user=user, status='expired')

            strike_text = "```No Previous Strikes```"
            if len(user_strikes) > 0:
                strike_messages = []

                for strike in user_strikes[:5]:
                    date = iso_to_datetime(strike['created_date']).strftime("%m/%d/%Y %H:%M")
                    issuer = strike['issuer'] if strike.get('issuer') else {'username': 'Unknown Issuer'}
                    strike_messages.append(f"{date} Strike by {issuer['username']} for {strike['reason'][0:90]} - {strike['_id']}")

                strike_text = "```" + "\r\n".join(strike_messages) + "```"

            info_message = f"<@{user.id}> was released by <@{context.author.id}>."
            if strike_info:
                info_message += "\r\n\r\nUser's last strike was deleted."

            fields = [
                {'name': 'Timeouts', 'value': f"{len(user_timeouts)} previous timeouts.", 'inline': True},
                {'name': 'Strikes', 'value': f"{len(user_strikes)} active strikes", 'inline': True},
                {'name': '\u200B', 'value': strike_text, 'inline': False}
            ]

            await self._bot.send_embed_message(context.log_channel, "Release user", info_message, fields=fields)

        # Send a DM to the user
        info_message = f"You've been released from the pit by {context.guild.name} mod staff."
        if strike_info:
                info_message += "\r\n\r\nYour last strike was additionally deleted."

        fields = [
            {'name': 'Strikes', 'value': f"You currently have {len(user_strikes)} active strikes in {context.guild.name}.", 'inline': False},
            {'name': 'Info', 'value': f"You can message me `pithistory` or `strikes` \
                to get a summary of your disciplinary history on {context.guild.name}.", 'inline': False}
        ]

        await self._bot.send_embed_dm(user.id, "User Timeout", info_message, fields=fields)

    async def send_help(self, context):
        fields = [
            {'name': '<amend>', 'value': "If `amend` is provided after user ping, it will delete the last strike issued from a Timeout.", 'inline': False},
            {'name': 'Example', 'value': f"{context.command_character}release <@{self._bot.user.id}> amend", 'inline': False}
        ]
        await self._bot.send_embed_message(context.log_channel, "Release User", 
            f"Use {context.command_character}release @user <amend:optional> will release a user from an active timeout.", fields=fields)
