# -*- coding: utf-8 -*-

## Release ##
# A command to release people. #

from discord.errors import NotFound

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class Watch(Command):
    @verify_permission
    async def execute(self, context: CommandContext) -> None:
        if len(context.params) == 0:
            await self.send_help(context)
            return

        user = None

        # We either need a mention or an ID as first parameter.
        if not context.mentions:
            user_id = context.params[0]
            if '@' in user_id:
                user_id = user_id[2:-1]
            # review its a "valid" snowflake
            if not len(user_id) > 16:
                await self.send_help(context)
                return
            user = self._module.get_user(user_id=user_id)
            if not user:
                user = int(user_id)
        else:
            user = context.mentions[0]

        try:
            if isinstance(user, int):
                user = await self._bot.get_guild(context.guild.id).fetch_member(user)
            elif isinstance(user, dict):
                user = await self._bot.get_guild(context.guild.id).fetch_member(int(user['discord_id']))
        except NotFound:
            try:
                if isinstance(user, int):
                    user = await self._bot.fetch_user(user)
                elif isinstance(user, dict):
                    user = await self._bot.fetch_user(int(user['discord_id']))
            except NotFound:
                fields = [
                    {'name': 'Error', 'value': f"User {user} doesn't exist.", 'inline': True},
                ]
                await self._bot.send_embed_message(context.log_channel, "Watch user", color=0xb30000, fields=fields)
                return
            fields = [
                {'name': 'Warning', 'value': f"User {user} is not in the server.", 'inline': True},
            ]
            await self._bot.send_embed_message(context.log_channel, "Watch user", color=0xffa500, fields=fields)
        if not user:
            return
        reason = ''
        if len(context.params) >= 1:
            reason = ' '.join(context.params[1:])
        self._module.create_watchlist_entry(user=user, guild_id=context.guild.id, issuer_id=context.author.id, reason=reason)

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'create_watchlist_entry'}, context=context)

        if not context.is_silent and context.log_channel:
            info_message = f"<@{user.id}> was added to the watchlist."
            await self._bot.send_embed_message(context.log_channel, "Watchlist", info_message)
