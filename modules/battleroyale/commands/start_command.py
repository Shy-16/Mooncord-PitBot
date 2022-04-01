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

	def __init__(self, br, permission: str ='mod', dm_keywords: list = list()) -> None:
		super().__init__(br, permission, dm_keywords)

	@verify_permission
	async def execute(self, context: CommandContext) -> None:

		# check if there is a number as parameter
		if len(context.params) > 0 and context.params[0].isnumeric():
			self._module._max_participants = context.params[0]

		# First send rules message
		content = '''
		**Mooncord Battle Royale**

		Starting now!
		'''

		await self._bot.send_embed_message(context.channel_id, "Battle Royale", content)

		self._module._started = True
		self._module.generate_event.start()
