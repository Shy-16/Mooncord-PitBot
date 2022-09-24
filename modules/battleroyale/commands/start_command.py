# -*- coding: utf-8 -*-

## SetupBRCommand Command ##
# A command to setup BR event. #

import asyncio
import discord
import random
import json

from modules.context import CommandContext
from modules.command import Command, verify_permission
from log_utils import do_log


class StartBRCommand(Command):
    """
    !start_br
    """

    def __init__(self, br, permission: str = 'mod', dm_keywords: list = list()) -> None:
        super().__init__(br, permission, dm_keywords)

    @verify_permission
    async def execute(self, context: CommandContext) -> None:

        # disable button so players can't join after it starts
        await self._module.disable_setup_button()

        # First send rules message
        content = '''
        **Mooncord Battle Royale**

        Starting now!
        '''

        await self._bot.send_embed_message(context.channel_id, "Battle Royale", content)

        self._module.game._started = True
