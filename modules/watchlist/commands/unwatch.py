# -*- coding: utf-8 -*-

## UnWatch ##
# Remove a user from the Watchlist. #

from discord.errors import NotFound

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class UnWatch(Command):
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
        except NotFound as ex:
            print(ex)
            fields = [
                {'name': 'Error', 'value': f"User {user} is not in the server and cannot be unwatched.", 'inline': True},
            ]
            await self._bot.send_embed_message(context.log_channel, "UnWatch user", color=0xb30000, fields=fields)
            return

        self._module.delete_watchlist_entry(user=user)

        await do_log(place="guild", data_dict={'event': 'command', 'command': 'release'}, context=context)

        if not context.is_silent and context.log_channel:
            info_message = f"<@{user.id}> was removed from the watchlist."
            await self._bot.send_embed_message(context.log_channel, "Watchlist", info_message)

    async def send_help(self, context):
        fields = [
            {'name': 'Example', 'value': f"{context.command_character}uw <@{self._bot.user.id}>", 'inline': False}
        ]
        await self._bot.send_embed_message(context.log_channel, "UnWatch User", 
            f"Use {context.command_character}uw @user will remove a user from the watchlist.", fields=fields)
