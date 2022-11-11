# -*- coding: utf-8 -*-

## Shutdown ##
# Turn off the bot. #

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class Shutdown(Command):
    @verify_permission
    async def execute(self, context: CommandContext) -> None:
        await do_log(place="guild", data_dict={'event': 'command', 'command': 'shutdown'}, context=context)

        await self._bot.send_embed_message(context.log_channel, "Shutdown",
            f'Shutting down issued by <@{context.author.id}>.\r\nYou need to start me again from command line.')

        await self._bot.close()


    async def send_help(self, context):
        description = f"Use {context.command_character}shutdown to kill the bot."

        fields = [
            {'name': 'Example', 'value': f"{context.command_character}shutdown", 'inline': False}
        ]

        await self._bot.send_embed_message(context.channel, "Shutdown", description, fields=fields)
