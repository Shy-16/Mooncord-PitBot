# -*- coding: utf-8 -*-

## Watchlist ##
# Prints the entire watchlist. #

from datetime import datetime

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class WatchListCommand(Command):
    def __init__(self, pitbot, permission: str ='mod', dm_keywords: list = None, skip_strike: bool =False) -> None:
        super().__init__(pitbot, permission, dm_keywords)
        self.skip_strike = skip_strike

    @verify_permission
    async def execute(self, context: CommandContext) -> None:
        watchlist = self._module.get_watchlist(status="active")
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'watchlist'}, context=context)
        if context.log_channel:
            userlist = "\r\n".join([f"<@{entry['user_id']}> ({entry['user_id']})\r\n\
                                    {entry['reason'] or '*No reason given*'}\r\n\
                                    {datetime.fromisoformat(entry['created_date']).strftime('%Y-%m-%d')} - <@{entry['issuer_id']}>\r\n" 
                                    for entry in watchlist[:30]])
            if not userlist or len(userlist) == 0:
                userlist = "*There are no users in the watchlist*"
            await self._bot.send_embed_message(context.log_channel, "Watchlist", userlist)

    async def send_help(self, context):
        fields = [
            {'name': 'watchlist | wl', 'value': f"{context.command_character}wl will show all watchlist.", 'inline': False},
            {'name': 'watch | wa', 'value': f"{context.command_character}wa will add a user to watchlist.", 'inline': False},
            {'name': 'unwatch | uw | wr', 'value': f"{context.command_character}uw will remove a user from watchlist.", 'inline': False},
        ]
        await self._bot.send_embed_message(context.channel, "Watchlist", fields=fields)
