# -*- coding: utf-8 -*-

## RouletteCommand ##
# A command to randomly timeout someone. #

from modules.context import CommandContext
from modules.command import Command, verify_permission


class ExecuteCommand(Command):
    """@Pit Bot execute order 66"""
    @verify_permission
    async def ping(self, context: CommandContext):
        # react to message
        await context.message.add_reaction("✅")

        # send a message back
        await self._bot.send_message(context.channel, "Executing order 66. No one shall be spared, not even the children.")
